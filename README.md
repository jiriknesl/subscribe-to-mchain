# Markov Chain User Behavior Simulator

This FastAPI application simulates user behaviors using Markov Chains and allows agents to register webhooks to be notified of simulated user actions.

## Features

- Create and manage Markov Chains to simulate user behavior
- Register and unregister agents with webhooks
- Run simulations with configurable steps
- Notify agents of simulated user actions
- Collect and aggregate agent responses

## Requirements

- Python 3.12 or higher
- PostgreSQL (for production use)

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

When running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exposing Agents for Webhooks during Development

When developing agents locally, you'll need to make your agent endpoints accessible to the simulator. Here are several approaches:

### Using Ngrok

[Ngrok](https://ngrok.com/) is a tool that creates a secure tunnel to expose your local server to the internet, allowing the simulator to send webhook calls to your local agent.

1. Install ngrok:
   ```bash
   # Using Homebrew on macOS
   brew install ngrok
   
   # Using Chocolatey on Windows
   choco install ngrok
   
   # Using npm
   npm install ngrok -g
   ```

2. Start your agent application (e.g., on port 8001):
   ```bash
   uvicorn examples.agent_counter:app --port 8001
   ```

3. In a separate terminal, start ngrok to expose port 8001:
   ```bash
   ngrok http 8001
   ```

4. You'll receive a public URL (e.g., `https://abc123.ngrok.io`) that you can use when registering your agent:
   ```python
   response = requests.post(
       "http://localhost:8000/agents/register",
       json={
           "url": "https://abc123.ngrok.io",  # Your ngrok URL
           "name": "My Agent",
           "description": "An agent that counts requests"
       }
   )
   ```

### Using localtunnel

[Localtunnel](https://github.com/localtunnel/localtunnel) is an alternative to ngrok:

1. Install localtunnel:
   ```bash
   npm install -g localtunnel
   ```

2. Start your agent application (e.g., on port 8001):
   ```bash
   uvicorn examples.agent_counter:app --port 8001
   ```

3. In a separate terminal, start localtunnel:
   ```bash
   lt --port 8001
   ```

4. Use the provided URL when registering your agent.

### Local Testing (Same Machine)

If both the simulator and agent are running on the same machine, you can simply use `localhost` URLs:

1. Start your agent:
   ```bash
   uvicorn examples.agent_counter:app --port 8001
   ```

2. Register your agent using the localhost URL:
   ```python
   response = requests.post(
       "http://localhost:8000/agents/register",
       json={
           "url": "http://localhost:8001",
           "name": "My Agent",
           "description": "An agent that counts requests"
       }
   )
   ```

## Example Usage

### 1. Register an Agent

```python
import requests

response = requests.post(
    "http://localhost:8000/agents/register",
    json={
        "url": "https://your-webhook-endpoint.com/hook",
        "name": "My Agent",
        "description": "An agent that counts requests"
    }
)
agent_data = response.json()
agent_id = agent_data["id"]
```

### 2. Create a Markov Chain

```python
response = requests.post(
    "http://localhost:8000/markov-chains",
    json={
        "states": {
            "homepage": {
                "name": "homepage",
                "transitions": {"product": 0.7, "cart": 0.3},
                "http_method": "GET",
                "payload": {}
            },
            "product": {
                "name": "product",
                "transitions": {"cart": 0.6, "homepage": 0.4},
                "http_method": "POST",
                "payload": {"product_id": 123}
            },
            "cart": {
                "name": "cart",
                "transitions": {"checkout": 0.8, "homepage": 0.2},
                "http_method": "GET",
                "payload": {}
            },
            "checkout": {
                "name": "checkout",
                "transitions": {"homepage": 1.0},
                "http_method": "POST",
                "payload": {"payment_method": "credit_card"}
            }
        },
        "initial_state": "homepage"
    }
)
chain_id = response.json()["id"]
```

### 3. Run a Simulation

```python
response = requests.post(
    "http://localhost:8000/simulate",
    json={
        "steps": 10,
        "chain_id": chain_id
    }
)
simulation_results = response.json()
```

### 4. Unregister an Agent

```python
response = requests.delete(f"http://localhost:8000/agents/{agent_id}")
```

## Tasks for Candidates

1. Create an agent that counts the number of GET requests
2. Implement an agent that responds differently based on the HTTP method
3. Build an agent that tracks the most common payload values
4. Develop an agent that maintains a session across requests
5. Create an agent that responds with a recommendation based on previous requests
6. Implement an agent that detects and alerts on unusual patterns
7. Build an agent that simulates form submissions only when specific conditions are met

## License

MIT 