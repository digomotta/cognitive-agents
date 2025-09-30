# Markov Agent Simulation Frontend

Real-time web visualization for multi-agent Markov chain simulations.

## Features

- **Agent Selection**: Browse and select agents from your population
- **Network Visualization**: D3.js force-directed graph showing agent connections
  - Node size = sales volume
  - Node color = net value (red to green)
  - Edge thickness = transition probability
- **Live Feed**: Real-time stream of:
  - Agent utterances (conversations)
  - Trade executions
  - Agent reflections
- **Leaderboard**: Rankings by sales, purchases, and net value
- **Status Panel**: Real-time event counts and simulation status

## Running the Frontend

### 1. Install Dependencies

```bash
pip install flask flask-cors
```

### 2. Start the Server

```bash
cd frontend
python app.py
```

### 3. Open in Browser

Navigate to: http://localhost:5002

## Usage

### Setup Page

1. **Select Agents**: Click on agent cards to select (minimum 2 required)
2. **Configure Simulation**:
   - Number of Steps: Total Markov chain steps
   - Max Turns: Maximum turns per conversation
   - Self-Reflection Probability: Chance of agent reflecting vs interacting
   - Interaction Probability: Distributed across other agents
   - Context: Overall simulation context
3. **Start Simulation**: Click "Start Simulation" button

### Simulation Page

Once started, you'll see:

- **Network Graph** (top): Agents as nodes, probabilities as edges
  - Drag nodes to rearrange
  - Node size shows sales volume
  - Color shows profit (green) vs loss (red)

- **Live Feed** (bottom): Scrolling messages
  - Blue border = agent utterance
  - Green border = trade execution
  - Yellow border = agent reflection
  - Auto-scrolls to latest

- **Leaderboard** (right side): Agent rankings
  - 🥇🥈🥉 for top 3
  - Shows sales, purchases, net value

- **Status Panel** (right side): Metrics
  - Simulation status
  - Event counts

## API Endpoints

- `GET /api/agents` - List all agents with details
- `GET /api/agent/<id>` - Get specific agent details
- `POST /api/simulation/start` - Start simulation
- `GET /api/simulation/status` - Get simulation status
- `POST /api/simulation/stop` - Stop simulation
- `GET /api/events` - Poll for new events (drains queue)
- `GET /api/leaderboard` - Get current leaderboard
- `GET /api/network` - Get network graph data

## Architecture

```
Frontend (Browser)
    ↓ Poll every 1s
Flask API
    ↓ Access event queue
MarkovAgentChain
    ↓ Emit events
Agents (conversations/trades/reflections)
```

Events flow from agents → queue → API → frontend in real-time.

## Customization

### Change Port

Edit `app.py` line 246:
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```

### Adjust Polling Rate

Edit `static/simulation.js` line 243:
```javascript
}, 1000); // Poll every 1 second
```

### Network Update Frequency

Edit `static/simulation.js` line 236:
```javascript
if (eventCounts.total % 10 === 0) {  // Every 10 events
```

## Troubleshooting

**No agents showing**: Check that `agent_bank/populations/Synthetic/` has agent folders

**Simulation starts but no events**: Check backend console for errors

**Network graph not updating**: Ensure D3.js CDN is accessible

**Events not appearing**: Check browser console for polling errors