"""
Models for agents and webhooks.

This module defines the Pydantic models used for representing agents
that can register webhooks to be notified of simulated user actions.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Agent(BaseModel):
    """Represents an agent that can register webhooks."""
    
    id: UUID = Field(default_factory=uuid4)
    url: HttpUrl
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = True
    
    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    """Model for creating a new agent."""
    
    url: HttpUrl
    name: str
    description: Optional[str] = None


class AgentUpdate(BaseModel):
    """Model for updating an existing agent."""
    
    url: Optional[HttpUrl] = None
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class AgentResponse(BaseModel):
    """Model for responses from agents during simulation."""
    
    agent_id: UUID
    agent_name: str
    data: Dict[str, Any]
    http_status: int
    latency_ms: float


class SimulationStep(BaseModel):
    """Model for a step in a simulation."""
    
    state_name: str
    http_method: str
    payload: Dict[str, Any]
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now) 