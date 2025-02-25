# Markov Chain User Behavior Simulator

This FastAPI application simulates user behaviors using Markov Chains and allows agents to register webhooks to be notified of simulated user actions.

## Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/subscribe-to-mchain.git
cd subscribe-to-mchain

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Main Simulator

```bash
# Start the main application
uvicorn app.main:app --reload
```

The simulator will automatically create a default e-commerce Markov chain on startup. You can access the API at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Running an Agent (Worker)

In a new terminal window, start the example agent:

```bash
# Activate the virtual environment (if not already activated)
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the example counter agent on port 8001
uvicorn examples.agent_counter:app --port 8001
```

The agent will automatically register itself with the simulator on startup. You can verify this by checking:
- Agent status: http://localhost:8001/status

### 4. Running a Simulation

#### Option 1: Using the Default Chain ID Endpoint

```bash
# Get the default chain ID
DEFAULT_CHAIN=$(curl -s http://localhost:8000/default-chain | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Run a simulation with 20 steps
curl -X POST http://localhost:8000/simulate/ \
  -H "Content-Type: application/json" \
  -d "{\"chain_id\": \"$DEFAULT_CHAIN\", \"steps\": 20}"
```

#### Option 2: Using a Direct Command

```bash
# Run a simulation with a specific chain ID (replace with your actual chain ID)
curl -X POST http://localhost:8000/simulate/ \
  -H "Content-Type: application/json" \
  -d '{"chain_id": "d733faf0-3cda-483d-978c-bccc2fc06306", "steps": 20}'
```

#### Option 3: Using the Swagger UI

1. Open http://localhost:8000/docs in your browser
2. Navigate to the `/simulate/` POST endpoint
3. Click "Try it out"
4. Enter the chain ID and number of steps
5. Click "Execute"

### 5. Checking Agent Results

```bash
# Check the agent's status and counters
curl http://localhost:8001/status

# Reset the agent's counters if needed
curl http://localhost:8001/reset
```

## Monitoring and Debugging

- The agent logs all incoming webhook calls to the console
- You can watch the agent's terminal to see real-time activity
- The simulator's logs will show information about the default chain creation

## API Overview

### Main Simulator Endpoints

- `GET /markov-chains/` - List all Markov chains
- `POST /markov-chains/` - Create a new chain
- `GET /default-chain` - Get the default chain ID
- `POST /simulate/` - Run a simulation
- `GET /agents/` - List all registered agents

### Agent Endpoints

- `GET /` - Endpoint that receives webhook calls
- `GET /status` - Check agent status and counters
- `GET /reset` - Reset agent counters

## Troubleshooting

- If the agent doesn't register, make sure the simulator is running first
- If simulations don't trigger agent calls, check that the agent URL is accessible
- If the application won't start, ensure all Python dependencies are installed
- Watch the terminal output for any error messages

## Advanced Usage

See the API documentation at http://localhost:8000/docs for detailed information on creating custom Markov chains, registering custom agents, and advanced simulation options.

## Development

For local development, both the simulator and agent can run on the same machine using different ports. For more complex setups, see the "Exposing Agents for Webhooks during Development" section below.

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

## License

MIT 