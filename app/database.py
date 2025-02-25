"""
Database connection and models.

This module provides database connectivity and ORM models for the application.
For simplicity in testing and development, we're using an in-memory store,
but the code is structured to easily swap in a real database connection.
"""

import os
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from datetime import datetime

from app.models.markov import MarkovChain
from app.models.agent import Agent
from app.models.simulation import Simulation

# Simple in-memory database for development and testing
db = {
    "markov_chains": {},  # UUID -> MarkovChain
    "agents": {},         # UUID -> Agent
    "simulations": {},    # UUID -> Simulation
}

logger = logging.getLogger(__name__)


class Database:
    """Database access layer with in-memory store for development."""
    
    @staticmethod
    async def init_db() -> None:
        """Initialize the database."""
        logger.info("Initializing database")
        # In a real application, this would set up database connections

    # MarkovChain operations
    @staticmethod
    async def create_markov_chain(chain: MarkovChain) -> MarkovChain:
        """Create a new Markov chain."""
        db["markov_chains"][chain.id] = chain
        return chain
    
    @staticmethod
    async def get_markov_chain(chain_id: UUID) -> Optional[MarkovChain]:
        """Get a Markov chain by ID."""
        return db["markov_chains"].get(chain_id)
    
    @staticmethod
    async def get_all_markov_chains() -> List[MarkovChain]:
        """Get all Markov chains."""
        return list(db["markov_chains"].values())
    
    @staticmethod
    async def delete_markov_chain(chain_id: UUID) -> bool:
        """Delete a Markov chain by ID."""
        if chain_id in db["markov_chains"]:
            del db["markov_chains"][chain_id]
            return True
        return False
    
    # Agent operations
    @staticmethod
    async def create_agent(agent: Agent) -> Agent:
        """Create a new agent."""
        db["agents"][agent.id] = agent
        return agent
    
    @staticmethod
    async def get_agent(agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID."""
        return db["agents"].get(agent_id)
    
    @staticmethod
    async def get_all_agents() -> List[Agent]:
        """Get all agents."""
        return list(db["agents"].values())
    
    @staticmethod
    async def get_active_agents() -> List[Agent]:
        """Get all active agents."""
        return [agent for agent in db["agents"].values() if agent.active]
    
    @staticmethod
    async def update_agent(agent_id: UUID, data: Dict[str, Any]) -> Optional[Agent]:
        """Update an agent by ID."""
        if agent_id in db["agents"]:
            agent = db["agents"][agent_id]
            for key, value in data.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
            return agent
        return None
    
    @staticmethod
    async def delete_agent(agent_id: UUID) -> bool:
        """Delete an agent by ID."""
        if agent_id in db["agents"]:
            del db["agents"][agent_id]
            return True
        return False
    
    # Simulation operations
    @staticmethod
    async def create_simulation(simulation: Simulation) -> Simulation:
        """Create a new simulation."""
        db["simulations"][simulation.id] = simulation
        return simulation
    
    @staticmethod
    async def get_simulation(simulation_id: UUID) -> Optional[Simulation]:
        """Get a simulation by ID."""
        return db["simulations"].get(simulation_id)
    
    @staticmethod
    async def update_simulation(simulation_id: UUID, data: Dict[str, Any]) -> Optional[Simulation]:
        """Update a simulation by ID."""
        if simulation_id in db["simulations"]:
            simulation = db["simulations"][simulation_id]
            for key, value in data.items():
                if hasattr(simulation, key):
                    setattr(simulation, key, value)
            return simulation
        return None
    
    @staticmethod
    async def add_step_to_simulation(simulation_id: UUID, step: Any) -> Optional[Simulation]:
        """Add a step to a simulation."""
        if simulation_id in db["simulations"]:
            simulation = db["simulations"][simulation_id]
            simulation.steps.append(step)
            return simulation
        return None
    
    @staticmethod
    async def complete_simulation(simulation_id: UUID) -> Optional[Simulation]:
        """Mark a simulation as complete."""
        if simulation_id in db["simulations"]:
            simulation = db["simulations"][simulation_id]
            simulation.end_time = datetime.now()
            return simulation
        return None 