"""
Router for simulation operations.

This module provides API endpoints for creating and retrieving
simulations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.models.simulation import Simulation, SimulationCreate, SimulationResponse
from app.database import Database
from app.markov_simulator import MarkovSimulator
from app.default_chains import get_default_chain_ids

router = APIRouter(
    prefix="/simulations",
    tags=["simulations"],
)

# Create a global simulator instance
simulator = MarkovSimulator()


@router.post("/", response_model=Simulation)
async def create_simulation(simulation: SimulationCreate) -> Simulation:
    """
    Create a new simulation for a Markov chain.
    """
    # Check if the chain exists
    chain = await Database.get_markov_chain(simulation.chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail=f"Markov chain with ID {simulation.chain_id} not found")
    
    # Run the simulation
    simulation_result = await simulator.run_simulation(simulation.chain_id, simulation.steps)
    return simulation_result


@router.get("/{simulation_id}", response_model=Simulation)
async def get_simulation(simulation_id: UUID) -> Simulation:
    """
    Get a simulation by ID.
    """
    simulation = await Database.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail=f"Simulation with ID {simulation_id} not found")
    return simulation


@router.get("/", response_model=List[SimulationResponse])
async def get_all_simulations() -> List[SimulationResponse]:
    """
    Get all simulations.
    """
    # This would need a proper implementation in Database
    return []  # Placeholder


@router.post("/default/{chain_key}", response_model=Simulation)
async def run_default_simulation(
    chain_key: str, 
    steps: int = Query(10, ge=1, le=100, description="Number of simulation steps")
) -> Simulation:
    """
    Run a simulation with one of the default Markov chains.
    
    Args:
        chain_key: The key of the default chain (ecommerce, social_media, streaming)
        steps: Number of steps to simulate (1-100)
    """
    # Get the default chain IDs
    default_chains = get_default_chain_ids()
    
    if not default_chains:
        raise HTTPException(status_code=404, detail="No default chains have been initialized")
    
    if chain_key not in default_chains:
        valid_keys = ", ".join(default_chains.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Default chain '{chain_key}' not found. Valid keys: {valid_keys}"
        )
    
    # Get the chain ID and run the simulation
    chain_id = default_chains[chain_key]
    
    # Create the simulation request
    sim_create = SimulationCreate(chain_id=chain_id, steps=steps)
    
    # Run the simulation
    simulation_result = await simulator.run_simulation(sim_create.chain_id, sim_create.steps)
    return simulation_result


@router.post("/run-all-defaults", response_model=List[Simulation])
async def run_all_default_simulations(
    steps: int = Query(10, ge=1, le=100, description="Number of simulation steps")
) -> List[Simulation]:
    """
    Run simulations for all default Markov chains.
    
    Args:
        steps: Number of steps to simulate (1-100)
    """
    # Get the default chain IDs
    default_chains = get_default_chain_ids()
    
    if not default_chains:
        raise HTTPException(status_code=404, detail="No default chains have been initialized")
    
    results = []
    for chain_key, chain_id in default_chains.items():
        # Run the simulation for each default chain
        simulation_result = await simulator.run_simulation(chain_id, steps)
        results.append(simulation_result)
    
    return results 