"""
Router for agent operations.

This module provides API endpoints for creating, retrieving, updating,
and deleting agents.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.database import Database

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


@router.post("/register", response_model=Agent)
async def register_agent(agent: AgentCreate) -> Agent:
    """
    Register a new agent.
    """
    new_agent = Agent(**agent.model_dump())
    return await Database.create_agent(new_agent)


@router.get("/", response_model=List[Agent])
async def get_all_agents() -> List[Agent]:
    """
    Get all agents.
    """
    return await Database.get_all_agents()


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: UUID) -> Agent:
    """
    Get an agent by ID.
    """
    agent = await Database.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    return agent


@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: UUID, update_data: AgentUpdate) -> Agent:
    """
    Update an agent by ID.
    """
    # Only include non-None values
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    agent = await Database.update_agent(agent_id, update_dict)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    return agent


@router.delete("/{agent_id}", response_model=bool)
async def delete_agent(agent_id: UUID) -> bool:
    """
    Delete (unregister) an agent by ID.
    """
    deleted = await Database.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
    return deleted 