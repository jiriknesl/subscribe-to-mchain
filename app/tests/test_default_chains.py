"""
Tests for the default Markov chains.

This module contains tests for the default chains defined in the default_chains module.
"""

import pytest
from uuid import UUID
import asyncio

from app.models.markov import MarkovChain
from app.default_chains import (
    DEFAULT_CHAINS,
    ECOMMERCE_CHAIN,
    SOCIAL_MEDIA_CHAIN,
    STREAMING_PLATFORM_CHAIN,
    create_default_markov_chains,
    get_default_chain_ids
)
from app.database import Database


@pytest.fixture(autouse=True)
async def clear_database():
    """Clear the database before each test."""
    # Clear chains from in-memory database
    Database.db["markov_chains"] = {}
    # Reset the default_chain_ids dictionary
    from app.default_chains import default_chain_ids
    default_chain_ids.clear()
    
    # Set a fresh dictionary for default_chain_ids to avoid shared reference issues
    import app.default_chains
    app.default_chains.default_chain_ids = {}
    
    yield
    # Clean up after test
    Database.db["markov_chains"] = {}
    default_chain_ids.clear()
    app.default_chains.default_chain_ids = {}


def test_default_chains_structure():
    """Test that all default chains are correctly structured."""
    for key, chain in DEFAULT_CHAINS.items():
        assert "name" in chain, f"Chain {key} missing 'name' field"
        assert "description" in chain, f"Chain {key} missing 'description' field"
        assert "states" in chain, f"Chain {key} missing 'states' field"
        assert "initial_state" in chain, f"Chain {key} missing 'initial_state' field"
        
        # Make sure the initial state exists
        assert chain["initial_state"] in chain["states"], f"Initial state '{chain['initial_state']}' not in states for chain {key}"
        
        # Check that all transitions point to valid states
        for state_name, state in chain["states"].items():
            for transition_target in state["transitions"]:
                assert transition_target in chain["states"], (
                    f"Transition target '{transition_target}' from state '{state_name}' "
                    f"not found in states for chain {key}"
                )
            
            # Check that transitions sum to approximately 1.0
            total = sum(state["transitions"].values())
            assert 0.99 <= total <= 1.01, f"Transitions in state '{state_name}' don't sum to 1.0, got {total}"


@pytest.mark.asyncio
async def test_create_default_markov_chains():
    """Test creating default Markov chains."""
    # First run should create chains
    chains = await create_default_markov_chains()
    
    # Verify we got the expected number of chains
    assert len(chains) == len(DEFAULT_CHAINS), "Wrong number of chains created"
    
    # Verify all expected keys are present
    for key in DEFAULT_CHAINS.keys():
        assert key in chains, f"Chain key '{key}' missing from created chains"
        assert isinstance(chains[key], UUID), f"Chain ID for {key} is not a UUID"
    
    # Check that chains were actually created in the database
    db_chains = await Database.get_all_markov_chains()
    assert len(db_chains) == len(DEFAULT_CHAINS), "Wrong number of chains in database"
    
    # Verify that running it again doesn't duplicate chains
    chains2 = await create_default_markov_chains()
    assert len(chains2) == len(chains), "Number of chains changed on second run"
    
    # Verify IDs are the same
    for key in chains:
        assert chains[key] == chains2[key], f"Chain ID for {key} changed on second run"
    
    db_chains2 = await Database.get_all_markov_chains()
    assert len(db_chains2) == len(db_chains), "Number of chains in database changed on second run"


@pytest.mark.asyncio
async def test_get_default_chain_ids():
    """Test getting default chain IDs."""
    # Clear any existing chain IDs since it's a global dict
    from app.default_chains import default_chain_ids
    default_chain_ids.clear()
    
    # Verify we start with no IDs
    initial_ids = get_default_chain_ids()
    assert len(initial_ids) == 0, "Expected no chain IDs initially"
    
    # Create the chains
    await create_default_markov_chains()
    
    # Now we should get IDs
    ids = get_default_chain_ids()
    assert len(ids) == len(DEFAULT_CHAINS), "Wrong number of chain IDs returned"
    
    # Verify all expected keys are present
    for key in DEFAULT_CHAINS.keys():
        assert key in ids, f"Chain key '{key}' missing from chain IDs"
        assert isinstance(ids[key], UUID), f"Chain ID for {key} is not a UUID"


@pytest.mark.asyncio
async def test_default_chains_validation():
    """Test that all default chains pass model validation."""
    for key, chain_dict in DEFAULT_CHAINS.items():
        # Convert to a MarkovChain model - this will run validation
        try:
            from app.models.markov import State
            
            states_dict = {}
            for state_name, state_data in chain_dict["states"].items():
                states_dict[state_name] = State(**state_data)
            
            chain = MarkovChain(
                states=states_dict,
                initial_state=chain_dict["initial_state"],
                name=chain_dict["name"],
                description=chain_dict["description"]
            )
            
            # Additional assertions to check chain properties
            assert chain.name == chain_dict["name"], f"Name mismatch for chain {key}"
            assert chain.description == chain_dict["description"], f"Description mismatch for chain {key}"
            assert chain.initial_state == chain_dict["initial_state"], f"Initial state mismatch for chain {key}"
            assert len(chain.states) == len(chain_dict["states"]), f"State count mismatch for chain {key}"
            
        except Exception as e:
            pytest.fail(f"Chain validation failed for {key}: {str(e)}") 