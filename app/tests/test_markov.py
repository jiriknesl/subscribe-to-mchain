"""
Tests for the Markov chain model.

This module contains tests for the Markov chain model, including
validation of states and transitions.
"""

import pytest
from pydantic import ValidationError

from app.models.markov import MarkovChain, State


def test_state_validation():
    """Test that state validation works correctly."""
    # Valid state
    state = State(
        name="homepage",
        transitions={"product": 0.7, "cart": 0.3},
        http_method="GET",
        payload={}
    )
    assert state.name == "homepage"
    assert state.transitions == {"product": 0.7, "cart": 0.3}
    assert state.http_method == "GET"
    assert state.payload == {}
    
    # Invalid transitions (sum != 1.0)
    with pytest.raises(ValidationError):
        State(
            name="homepage",
            transitions={"product": 0.7, "cart": 0.2},  # Sum = 0.9
            http_method="GET",
            payload={}
        )
    
    # Invalid HTTP method
    with pytest.raises(ValidationError):
        State(
            name="homepage",
            transitions={"product": 0.7, "cart": 0.3},
            http_method="INVALID",  # Not a valid HTTP method
            payload={}
        )


def test_markov_chain_validation():
    """Test that Markov chain validation works correctly."""
    # Valid Markov chain
    chain = MarkovChain(
        states={
            "homepage": State(
                name="homepage",
                transitions={"product": 0.7, "cart": 0.3},
                http_method="GET",
                payload={}
            ),
            "product": State(
                name="product",
                transitions={"cart": 0.6, "homepage": 0.4},
                http_method="POST",
                payload={"product_id": 123}
            ),
            "cart": State(
                name="cart",
                transitions={"homepage": 1.0},
                http_method="GET",
                payload={}
            )
        },
        initial_state="homepage"
    )
    assert chain.initial_state == "homepage"
    assert len(chain.states) == 3
    
    # Invalid initial state
    with pytest.raises(ValidationError):
        MarkovChain(
            states={
                "homepage": State(
                    name="homepage",
                    transitions={"product": 0.7, "cart": 0.3},
                    http_method="GET",
                    payload={}
                ),
            },
            initial_state="nonexistent"  # State doesn't exist
        )
    
    # Invalid transition target
    with pytest.raises(ValidationError):
        MarkovChain(
            states={
                "homepage": State(
                    name="homepage",
                    transitions={"nonexistent": 1.0},  # Target doesn't exist
                    http_method="GET",
                    payload={}
                ),
            },
            initial_state="homepage"
        ) 