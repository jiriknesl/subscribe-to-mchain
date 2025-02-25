"""
Main application entry point.

This module initializes the FastAPI application, sets up middleware,
configures routes, and starts the server when run directly.
"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database import Database
from app.routers import markov, agent, simulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

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


# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    await Database.init_db()
    logging.info("Application started")


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Include routers
app.include_router(markov.router)
app.include_router(agent.router)
app.include_router(simulation.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 