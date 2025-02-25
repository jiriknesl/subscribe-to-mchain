"""
Example agent that counts requests.

This is a simple FastAPI application that demonstrates how to create an agent
that counts requests from the Markov Chain simulator. It registers itself
with the simulator and counts the number of GET, POST, and other requests.

To run this example:
1. Start the simulator: `uvicorn app.main:app --reload`
2. Start this agent: `uvicorn examples.agent_counter:app --port 8001`
3. Register the agent with the simulator
4. Create a Markov chain
5. Run a simulation
"""

import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI()

# Simple in-memory counter
counters = {
    "GET": 0,
    "POST": 0,
    "PUT": 0,
    "DELETE": 0,
    "PATCH": 0,
    "total": 0
}


class CounterResponse(BaseModel):
    """Response model for the counter agent."""
    counters: Dict[str, int]
    method: str
    path: str
    payload: Optional[Dict[str, Any]] = None


@app.get("/")
async def handle_get(request: Request):
    """Handle GET requests from the simulator."""
    logging.info(f"Received GET request: {request.query_params}")
    
    # Increment counters
    counters["GET"] += 1
    counters["total"] += 1
    
    # Get query parameters
    params = dict(request.query_params)
    
    return CounterResponse(
        counters=counters.copy(),
        method="GET",
        path=request.url.path,
        payload=params
    )


@app.post("/")
async def handle_post(request: Request):
    """Handle POST requests from the simulator."""
    logging.info("Received POST request")
    
    # Increment counters
    counters["POST"] += 1
    counters["total"] += 1
    
    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    
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
    logging.info(f"Received {method} request")
    
    # Increment counters
    if method in counters:
        counters[method] += 1
    counters["total"] += 1
    
    # Parse JSON payload for non-GET requests
    try:
        payload = await request.json() if method != "GET" else dict(request.query_params)
    except Exception:
        payload = {}
    
    return CounterResponse(
        counters=counters.copy(),
        method=method,
        path=request.url.path,
        payload=payload
    )


@app.get("/reset")
async def reset_counters():
    """Reset all counters."""
    for key in counters:
        counters[key] = 0
    return {"message": "Counters reset", "counters": counters}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 