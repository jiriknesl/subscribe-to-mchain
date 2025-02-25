"""
Router for simulation operations.

This module provides API endpoints for running and retrieving simulations.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.models.simulation import Simulation, SimulationCreate, SimulationResponse
from app.markov_simulator import MarkovSimulator
from app.database import Database

router = APIRouter(
    prefix="/simulate",
    tags=["simulation"],
)

# Create a global simulator instance
simulator = MarkovSimulator()


@router.post("/", response_model=SimulationResponse)
async def run_simulation(simulation_data: SimulationCreate) -> SimulationResponse:
    """
    Run a new simulation.
    """
    # Check if the Markov chain exists
    chain = await Database.get_markov_chain(simulation_data.chain_id)
    if not chain:
        raise HTTPException(
            status_code=404, 
            detail=f"Markov chain with ID {simulation_data.chain_id} not found"
        )
    
    # Run the simulation
    simulation = await simulator.run_simulation(
        chain_id=simulation_data.chain_id,
        num_steps=simulation_data.steps
    )
    
    # Convert to response model
    return SimulationResponse(
        id=simulation.id,
        chain_id=simulation.chain_id,
        steps=simulation.steps,
        start_time=simulation.start_time,
        end_time=simulation.end_time,
        total_steps=simulation.total_steps,
        duration_seconds=simulation.duration_seconds
    )


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: UUID) -> SimulationResponse:
    """
    Get a simulation by ID.
    """
    simulation = await Database.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(
            status_code=404, 
            detail=f"Simulation with ID {simulation_id} not found"
        )
    
    # Convert to response model
    return SimulationResponse(
        id=simulation.id,
        chain_id=simulation.chain_id,
        steps=simulation.steps,
        start_time=simulation.start_time,
        end_time=simulation.end_time,
        total_steps=simulation.total_steps,
        duration_seconds=simulation.duration_seconds
    ) 