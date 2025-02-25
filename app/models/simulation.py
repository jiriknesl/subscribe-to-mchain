"""
Models for simulations.

This module defines the Pydantic models used for representing 
simulations and their results.
"""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.models.agent import SimulationStep


class SimulationCreate(BaseModel):
    """Model for creating a new simulation."""
    
    chain_id: UUID
    steps: int = 10
    
    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: int) -> int:
        """Validate the number of steps."""
        assert 1 <= v <= 100, "Number of steps must be between 1 and 100"
        return v


class Simulation(BaseModel):
    """Represents a complete simulation with results."""
    
    id: UUID = Field(default_factory=uuid4)
    chain_id: UUID
    steps: List[SimulationStep] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def total_steps(self) -> int:
        """Get the total number of steps in the simulation."""
        return len(self.steps)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get the duration of the simulation in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class SimulationResponse(BaseModel):
    """Model for returning simulation results."""
    
    id: UUID
    chain_id: UUID
    steps: List[SimulationStep]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_steps: int
    duration_seconds: Optional[float] = None 