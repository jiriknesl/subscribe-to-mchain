"""
Example agent that counts requests.

This is a simple FastAPI application that demonstrates how to create an agent
that counts requests from the Markov Chain simulator. It registers itself
with the simulator automatically on startup and counts the number of GET, POST, 
and other requests.

To run this example:
1. Start the simulator: `uvicorn app.main:app --reload`
2. Start this agent: `uvicorn examples.agent_counter:app --port 8001`
3. The agent will register itself with the simulator
4. Create a Markov chain
5. Run a simulation
"""

import logging
import asyncio
import httpx
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Configure logging to show more details
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration
SIMULATOR_URL = "http://localhost:8000"
AGENT_URL = "http://localhost:8001"  # This agent's URL
AGENT_NAME = "Counter Agent"

# Simple in-memory counter
counters = {
    "GET": 0,
    "POST": 0,
    "PUT": 0,
    "DELETE": 0,
    "PATCH": 0,
    "total": 0
}

# Store agent ID after registration
agent_id = None


class CounterResponse(BaseModel):
    """Response model for the counter agent."""
    counters: Dict[str, int]
    method: str
    path: str
    payload: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """Register the agent with the simulator on startup."""
    global agent_id
    
    logger.info("🚀 Counter Agent starting up...")
    logger.info(f"Agent is running at {AGENT_URL}")
    
    # Try to register with the simulator
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Attempting to register with simulator at {SIMULATOR_URL}...")
            
            response = await client.post(
                f"{SIMULATOR_URL}/agents/register",
                json={
                    "url": AGENT_URL,
                    "name": AGENT_NAME,
                    "description": "An agent that counts different types of HTTP requests"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_id = data["id"]
                logger.info(f"✅ Successfully registered agent with ID: {agent_id}")
                logger.info("Waiting for webhook calls from the simulator...")
            else:
                logger.error(f"❌ Failed to register agent. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ Error during registration: {str(e)}")
        logger.info("The agent will continue running, but won't receive simulator calls.")
        logger.info("Make sure the simulator is running at the correct URL.")


@app.get("/")
async def handle_get(request: Request):
    """Handle GET requests from the simulator."""
    logger.info(f"📥 Received GET request from {request.client.host}")
    logger.info(f"   Query parameters: {dict(request.query_params)}")
    
    # Increment counters
    counters["GET"] += 1
    counters["total"] += 1
    
    # Get query parameters
    params = dict(request.query_params)
    
    logger.info(f"   Current counters: GET={counters['GET']}, total={counters['total']}")
    
    return CounterResponse(
        counters=counters.copy(),
        method="GET",
        path=request.url.path,
        payload=params
    )


@app.post("/")
async def handle_post(request: Request):
    """Handle POST requests from the simulator."""
    logger.info(f"📥 Received POST request from {request.client.host}")
    
    # Increment counters
    counters["POST"] += 1
    counters["total"] += 1
    
    # Parse JSON payload
    try:
        payload = await request.json()
        logger.info(f"   Payload: {json.dumps(payload)}")
    except Exception:
        payload = {}
        logger.info("   No valid JSON payload")
    
    logger.info(f"   Current counters: POST={counters['POST']}, total={counters['total']}")
    
    return CounterResponse(
        counters=counters.copy(),
        method="POST",
        path=request.url.path,
        payload=payload
    )


@app.put("/")
@app.delete("/")
@app.patch("/")
async def handle_other(request: Request):
    """Handle other HTTP methods from the simulator."""
    method = request.method
    logger.info(f"📥 Received {method} request from {request.client.host}")
    
    # Increment counters
    if method in counters:
        counters[method] += 1
    counters["total"] += 1
    
    # Parse JSON payload for non-GET requests
    try:
        payload = await request.json() if method != "GET" else dict(request.query_params)
        logger.info(f"   Payload: {json.dumps(payload)}")
    except Exception:
        payload = {}
        logger.info("   No valid payload")
    
    logger.info(f"   Current counters: {method}={counters.get(method, 0)}, total={counters['total']}")
    
    return CounterResponse(
        counters=counters.copy(),
        method=method,
        path=request.url.path,
        payload=payload
    )


@app.get("/reset")
async def reset_counters():
    """Reset all counters."""
    logger.info("🔄 Resetting all counters")
    
    for key in counters:
        counters[key] = 0
        
    return {"message": "Counters reset", "counters": counters}


@app.get("/status")
async def agent_status():
    """Get the agent's status."""
    return {
        "status": "running",
        "agent_id": agent_id,
        "agent_name": AGENT_NAME,
        "counters": counters,
        "registered": agent_id is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 