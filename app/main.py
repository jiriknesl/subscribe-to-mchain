"""
Main application entry point.

This module initializes the FastAPI application, sets up middleware,
configures routes, and starts the server when run directly.
"""

import logging
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database import Database
from app.routers import markov, agent, simulation
from app.models.markov import MarkovChain, State

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(
    title="Markov Chain User Behavior Simulator",
    description="A FastAPI application that simulates user behaviors using Markov Chains and allows agents to register webhooks.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Default e-commerce markov chain definition
DEFAULT_MARKOV_CHAIN = {
    "name": "E-commerce User Journey",
    "description": "A realistic simulation of user behavior on an e-commerce website",
    "states": {
        # Home page and navigation
        "homepage": {
            "name": "homepage",
            "transitions": {
                "category_listing": 0.35,
                "product_search": 0.25,
                "login": 0.15,
                "featured_product": 0.15,
                "cart": 0.05,
                "account": 0.05
            },
            "http_method": "GET",
            "payload": {}
        },
        
        # Category browsing
        "category_listing": {
            "name": "category_listing",
            "transitions": {
                "product_listing": 0.6,
                "category_filter": 0.2,
                "homepage": 0.1,
                "search_results": 0.1
            },
            "http_method": "GET",
            "payload": {"category_id": 123}
        },
        
        "category_filter": {
            "name": "category_filter",
            "transitions": {
                "product_listing": 0.7,
                "category_listing": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"category_id": 123, "filter": {"price_range": "100-200", "brand": "acme"}}
        },
        
        # Product browsing
        "product_listing": {
            "name": "product_listing",
            "transitions": {
                "product_detail": 0.6,
                "category_filter": 0.15,
                "category_listing": 0.1,
                "homepage": 0.05,
                "cart": 0.1
            },
            "http_method": "GET",
            "payload": {"page": 1, "sort": "popularity"}
        },
        
        "product_detail": {
            "name": "product_detail",
            "transitions": {
                "add_to_cart": 0.3,
                "product_reviews": 0.2,
                "product_listing": 0.2,
                "add_to_wishlist": 0.1,
                "homepage": 0.1,
                "related_product": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 1234}
        },
        
        "product_reviews": {
            "name": "product_reviews",
            "transitions": {
                "product_detail": 0.6,
                "write_review": 0.1,
                "product_listing": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 1234, "page": 1}
        },
        
        "related_product": {
            "name": "related_product",
            "transitions": {
                "product_detail": 0.7,
                "add_to_cart": 0.2,
                "product_listing": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 5678}
        },
        
        "featured_product": {
            "name": "featured_product",
            "transitions": {
                "product_detail": 0.7,
                "homepage": 0.2,
                "add_to_cart": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 9012}
        },
        
        # Search functionality
        "product_search": {
            "name": "product_search",
            "transitions": {
                "search_results": 0.8,
                "homepage": 0.2
            },
            "http_method": "POST",
            "payload": {"query": "smartphone", "filters": {}}
        },
        
        "search_results": {
            "name": "search_results",
            "transitions": {
                "product_detail": 0.5,
                "search_filter": 0.2,
                "product_search": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"query": "smartphone", "page": 1}
        },
        
        "search_filter": {
            "name": "search_filter",
            "transitions": {
                "search_results": 0.7,
                "product_detail": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"query": "smartphone", "filters": {"price_min": 300, "price_max": 800}}
        },
        
        # Cart and checkout
        "add_to_cart": {
            "name": "add_to_cart",
            "transitions": {
                "cart": 0.4,
                "product_detail": 0.3,
                "product_listing": 0.2,
                "checkout_shipping": 0.1
            },
            "http_method": "POST",
            "payload": {"product_id": 1234, "quantity": 1, "options": {"color": "black"}}
        },
        
        "add_to_wishlist": {
            "name": "add_to_wishlist",
            "transitions": {
                "product_detail": 0.7,
                "wishlist": 0.2,
                "product_listing": 0.1
            },
            "http_method": "POST",
            "payload": {"product_id": 1234}
        },
        
        "cart": {
            "name": "cart",
            "transitions": {
                "checkout_shipping": 0.3,
                "update_cart": 0.2,
                "product_detail": 0.2,
                "product_listing": 0.15,
                "homepage": 0.15
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "update_cart": {
            "name": "update_cart",
            "transitions": {
                "cart": 0.8,
                "checkout_shipping": 0.2
            },
            "http_method": "PATCH",
            "payload": {"items": [{"id": 9876, "quantity": 2}]}
        },
        
        "checkout_shipping": {
            "name": "checkout_shipping",
            "transitions": {
                "checkout_payment": 0.7,
                "cart": 0.3
            },
            "http_method": "POST",
            "payload": {
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip": "12345",
                    "country": "US"
                },
                "shipping_method": "standard"
            }
        },
        
        "checkout_payment": {
            "name": "checkout_payment",
            "transitions": {
                "checkout_review": 0.7,
                "checkout_shipping": 0.2,
                "cart": 0.1
            },
            "http_method": "POST",
            "payload": {"payment_method": "credit_card", "card_token": "tok_****"}
        },
        
        "checkout_review": {
            "name": "checkout_review",
            "transitions": {
                "place_order": 0.8,
                "checkout_payment": 0.1,
                "checkout_shipping": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "place_order": {
            "name": "place_order",
            "transitions": {
                "order_confirmation": 0.95,
                "checkout_review": 0.05
            },
            "http_method": "POST",
            "payload": {"confirm": True}
        },
        
        "order_confirmation": {
            "name": "order_confirmation",
            "transitions": {
                "homepage": 0.5,
                "account_orders": 0.3,
                "product_listing": 0.2
            },
            "http_method": "GET",
            "payload": {"order_id": "ORD-12345"}
        },
        
        # User account
        "login": {
            "name": "login",
            "transitions": {
                "homepage": 0.4,
                "account": 0.3,
                "cart": 0.2,
                "register": 0.1
            },
            "http_method": "POST",
            "payload": {"email": "user@example.com", "password": "********"}
        },
        
        "register": {
            "name": "register",
            "transitions": {
                "homepage": 0.5,
                "account": 0.3,
                "login": 0.2
            },
            "http_method": "POST",
            "payload": {
                "email": "newuser@example.com",
                "password": "********",
                "name": "New User"
            }
        },
        
        "account": {
            "name": "account",
            "transitions": {
                "account_orders": 0.25,
                "account_profile": 0.25,
                "wishlist": 0.2,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "account_profile": {
            "name": "account_profile",
            "transitions": {
                "update_profile": 0.3,
                "account": 0.4,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "update_profile": {
            "name": "update_profile",
            "transitions": {
                "account_profile": 0.6,
                "account": 0.4
            },
            "http_method": "PATCH",
            "payload": {"name": "Updated Name", "email": "updated@example.com"}
        },
        
        "account_orders": {
            "name": "account_orders",
            "transitions": {
                "order_details": 0.4,
                "account": 0.3,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "order_details": {
            "name": "order_details",
            "transitions": {
                "account_orders": 0.6,
                "write_review": 0.2,
                "account": 0.2
            },
            "http_method": "GET",
            "payload": {"order_id": "ORD-12345"}
        },
        
        "wishlist": {
            "name": "wishlist",
            "transitions": {
                "product_detail": 0.4,
                "account": 0.3,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        
        "write_review": {
            "name": "write_review",
            "transitions": {
                "product_detail": 0.5,
                "account_orders": 0.3,
                "order_details": 0.2
            },
            "http_method": "POST",
            "payload": {"product_id": 1234, "rating": 5, "comment": "Great product!"}
        }
    },
    "initial_state": "homepage"
}

# Store the default chain ID for easy access
default_chain_id = None

async def create_default_markov_chain():
    """Create a default Markov chain if none exist."""
    global default_chain_id
    
    chains = await Database.get_all_markov_chains()
    logger.info(f"Found {len(chains)} existing Markov chain(s)")
    
    if not chains:
        logger.info("No existing Markov chains found. Creating default e-commerce chain...")
        
        try:
            # Convert the dictionary to a MarkovChain model
            states_dict = {}
            for state_name, state_data in DEFAULT_MARKOV_CHAIN["states"].items():
                states_dict[state_name] = State(**state_data)
            
            chain = MarkovChain(
                states=states_dict,
                initial_state=DEFAULT_MARKOV_CHAIN["initial_state"],
                name=DEFAULT_MARKOV_CHAIN["name"],
                description=DEFAULT_MARKOV_CHAIN["description"]
            )
            
            # Create the chain in the database
            created_chain = await Database.create_markov_chain(chain)
            default_chain_id = created_chain.id
            
            logger.info(f"✅ Created default Markov chain with ID: {default_chain_id}")
            logger.info(f"Chain contains {len(chain.states)} states simulating e-commerce user behavior")
            
            # Double-check that it's retrievable
            retrieved_chain = await Database.get_markov_chain(default_chain_id)
            if retrieved_chain:
                logger.info(f"✅ Successfully verified chain retrieval for ID: {default_chain_id}")
            else:
                logger.error(f"❌ Failed to retrieve newly created chain with ID: {default_chain_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create default Markov chain: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        # Store the first chain's ID as default
        default_chain_id = chains[0].id
        logger.info(f"Using existing chain with ID: {default_chain_id} as default")


# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    await Database.init_db()
    logger.info("Database initialized")
    
    # Create default Markov chain
    await create_default_markov_chain()
    
    logger.info("Application started")


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Get default chain endpoint
@app.get("/default-chain", tags=["markov-chains"])
async def get_default_chain():
    """Get the default Markov chain ID."""
    if default_chain_id:
        return {"id": default_chain_id, "message": "Default chain is ready for use"}
    
    # If no default ID is set, try to get the first chain
    chains = await Database.get_all_markov_chains()
    if chains:
        return {"id": chains[0].id, "message": "Using first available chain as default"}
    
    return {"error": "No Markov chains found in the database"}


# Include routers
app.include_router(markov.router)
app.include_router(agent.router)
app.include_router(simulation.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 