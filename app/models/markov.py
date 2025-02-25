"""
Models for Markov chains and states.

This module defines the Pydantic models used for representing Markov chains,
their states, and transitions between states.
"""

from typing import Dict, Any, Optional, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, model_validator


class State(BaseModel):
    """Represents a state in a Markov chain with transition probabilities."""
    
    name: str
    transitions: Dict[str, float]
    http_method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("transitions")
    @classmethod
    def validate_transitions(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate that transition probabilities sum to approximately 1.0."""
        total = sum(v.values())
        assert 0.99 <= total <= 1.01, f"Transition probabilities must sum to approximately 1.0, got {total}"
        return v


class MarkovChain(BaseModel):
    """Represents a Markov chain with states and an initial state."""
    
    id: UUID = Field(default_factory=uuid4)
    states: Dict[str, State]
    initial_state: str
    name: Optional[str] = None
    description: Optional[str] = None
    
    @model_validator(mode="after")
    def validate_states_and_transitions(self) -> "MarkovChain":
        """
        Validate that:
        1. The initial state exists in states
        2. All transition targets exist in states
        """
        assert self.initial_state in self.states, f"Initial state '{self.initial_state}' not found in states"
        
        for state_name, state in self.states.items():
            for transition_target in state.transitions:
                assert transition_target in self.states, (
                    f"Transition target '{transition_target}' from state '{state_name}' "
                    f"not found in states"
                )
        
        return self


class MarkovChainCreate(BaseModel):
    """Model for creating a new Markov chain."""
    
    states: Dict[str, State]
    initial_state: str
    name: Optional[str] = None
    description: Optional[str] = None 