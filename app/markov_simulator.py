"""
Markov Chain simulator.

This module provides the implementation for simulating Markov chains
to model user behavior.
"""

import random
import asyncio
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import time
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.models.markov import MarkovChain, State
from app.models.agent import Agent, AgentResponse, SimulationStep
from app.models.simulation import Simulation
from app.database import Database

logger = logging.getLogger(__name__)


class MarkovSimulator:
    """Simulator for running Markov chain simulations."""
    
    def __init__(self, timeout: float = 5.0):
        """
        Initialize the simulator.
        
        Args:
            timeout: Timeout in seconds for webhook calls
        """
        self.timeout = timeout
    
    async def run_simulation(self, chain_id: UUID, num_steps: int) -> Simulation:
        """
        Run a simulation for the specified number of steps.
        
        Args:
            chain_id: The ID of the Markov chain to simulate
            num_steps: The number of steps to simulate
            
        Returns:
            A Simulation object with results
        """
        chain = await Database.get_markov_chain(chain_id)
        if not chain:
            raise HTTPException(status_code=404, detail=f"Markov chain with ID {chain_id} not found")
        
        agents = await Database.get_active_agents()
        
        # Create a new simulation
        simulation = Simulation(chain_id=chain_id)
        await Database.create_simulation(simulation)
        
        # Start the simulation
        current_state_name = chain.initial_state
        
        for _ in range(num_steps):
            # Get the current state
            current_state = chain.states[current_state_name]
            
            # Create a simulation step
            step = await self._execute_step(current_state, agents)
            
            # Add the step to the simulation
            await Database.add_step_to_simulation(simulation.id, step)
            
            # Choose the next state
            current_state_name = self._choose_next_state(current_state)
        
        # Mark the simulation as complete
        simulation = await Database.complete_simulation(simulation.id)
        assert simulation is not None, "Simulation was unexpectedly removed during execution"
        
        return simulation
    
    async def _execute_step(self, state: State, agents: List[Agent]) -> SimulationStep:
        """
        Execute a single step of the simulation.
        
        Args:
            state: The current state
            agents: List of active agents to notify
            
        Returns:
            A SimulationStep with results
        """
        step = SimulationStep(
            state_name=state.name,
            http_method=state.http_method,
            payload=state.payload
        )
        
        # Notify all agents in parallel
        agent_responses = await asyncio.gather(
            *[self._notify_agent(agent, state.http_method, state.payload) for agent in agents],
            return_exceptions=True
        )
        
        # Process agent responses
        for i, response in enumerate(agent_responses):
            if isinstance(response, Exception):
                logger.warning(f"Error notifying agent {agents[i].id}: {str(response)}")
                continue
            
            if response:
                step.agent_responses.append(response)
        
        return step
    
    async def _notify_agent(self, agent: Agent, method: str, payload: Dict[str, Any]) -> AgentResponse:
        """
        Notify an agent of a state transition.
        
        Args:
            agent: The agent to notify
            method: The HTTP method to use
            payload: The payload to send
            
        Returns:
            An AgentResponse with the agent's response
        """
        assert agent.active, f"Agent {agent.id} is not active"
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(
                        str(agent.url), 
                        params=payload,
                        headers={"X-Simulation": "true"}
                    )
                else:
                    response = await client.request(
                        method=method,
                        url=str(agent.url),
                        json=payload,
                        headers={"X-Simulation": "true", "Content-Type": "application/json"}
                    )
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                try:
                    data = response.json()
                except Exception:
                    data = {"raw_response": response.text}
                
                return AgentResponse(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    data=data,
                    http_status=response.status_code,
                    latency_ms=latency_ms
                )
        except Exception as e:
            logger.warning(f"Error notifying agent {agent.id}: {str(e)}")
            raise
    
    def _choose_next_state(self, current_state: State) -> str:
        """
        Choose the next state based on transition probabilities.
        
        Args:
            current_state: The current state
            
        Returns:
            The name of the next state
        """
        if not current_state.transitions:
            return current_state.name
        
        rand = random.random()
        cumulative = 0.0
        
        for state_name, probability in current_state.transitions.items():
            cumulative += probability
            if rand <= cumulative:
                return state_name
        
        # Fallback in case of floating point rounding issues
        return list(current_state.transitions.keys())[-1] 