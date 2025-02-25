"""
Router for Markov chain operations.

This module provides API endpoints for creating, retrieving, and
managing Markov chains.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.models.markov import MarkovChain, MarkovChainCreate
from app.database import Database

router = APIRouter(
    prefix="/markov-chains",
    tags=["markov-chains"],
)


@router.post("/", response_model=MarkovChain)
async def create_markov_chain(chain: MarkovChainCreate) -> MarkovChain:
    """
    Create a new Markov chain.
    """
    markov_chain = MarkovChain(**chain.model_dump())
    return await Database.create_markov_chain(markov_chain)


@router.get("/", response_model=List[MarkovChain])
async def get_all_markov_chains() -> List[MarkovChain]:
    """
    Get all Markov chains.
    """
    return await Database.get_all_markov_chains()


@router.get("/{chain_id}", response_model=MarkovChain)
async def get_markov_chain(chain_id: UUID) -> MarkovChain:
    """
    Get a Markov chain by ID.
    """
    chain = await Database.get_markov_chain(chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail=f"Markov chain with ID {chain_id} not found")
    return chain


@router.delete("/{chain_id}", response_model=bool)
async def delete_markov_chain(chain_id: UUID) -> bool:
    """
    Delete a Markov chain by ID.
    """
    deleted = await Database.delete_markov_chain(chain_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Markov chain with ID {chain_id} not found")
    return deleted 