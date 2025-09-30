"""
Flask Backend for Markov Agent Chain Visualization

Provides REST API and serves frontend for real-time simulation visualization.
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import threading
import time
import sys
import os
from typing import Optional

# Add parent directory to path to import project modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from simulation_engine.markov_agent_chain import MarkovAgentChain, load_agents_for_chain
from generative_agent.generative_agent import GenerativeAgent

app = Flask(__name__)
CORS(app)

# Global simulation state
simulation_thread: Optional[threading.Thread] = None
markov_chain: Optional[MarkovAgentChain] = None
simulation_running = False
simulation_agents = []
simulation_agents_loaded = []  # Store loaded agent objects
simulation_config = {}
simulation_transition_matrix = None


def run_simulation_background(agent_names, num_steps, context, self_reflection_prob, interaction_prob, max_turns):
    """Run simulation in background thread."""
    global simulation_running, markov_chain, simulation_agents_loaded, simulation_transition_matrix

    try:
        print(f"Starting simulation with {len(agent_names)} agents for {num_steps} steps")

        # Load agents
        agents = load_agents_for_chain("Synthetic", agent_names)

        if len(agents) < 2:
            print("Error: Need at least 2 agents")
            simulation_running = False
            return

        # Store loaded agents globally
        simulation_agents_loaded = agents

        # Run simulation
        results = markov_chain.run_markov_chain(
            agents=agents,
            context=context,
            num_steps=num_steps,
            self_reflection_prob=self_reflection_prob,
            interaction_prob=interaction_prob,
            conversation_max_turns=max_turns,
            testing_mode=True
        )

        # Store transition matrix
        simulation_transition_matrix = results.get('transition_matrix')

        print(f"Simulation completed: {results['conversation_count']} conversations, {results['reflection_count']} reflections")

    except Exception as e:
        print(f"Simulation error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        simulation_running = False


@app.route('/')
def index():
    """Serve main page."""
    return render_template('simulation.html')


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of available agents with their details."""
    population = request.args.get('population', 'Synthetic')

    # Get available agents from the population directory
    population_path = os.path.join(parent_dir, "agent_bank", "populations", population)

    if not os.path.exists(population_path):
        return jsonify({'error': 'Population not found'}), 404

    agents_data = []

    # List directories in population
    for agent_id in os.listdir(population_path):
        agent_dir = os.path.join(population_path, agent_id)
        if os.path.isdir(agent_dir):
            try:
                # Load agent to get details
                agent = GenerativeAgent(population, agent_id)

                # Safely get occupation
                occupation = getattr(agent.scratch, 'occupation', None)
                if not occupation:
                    # Try to extract from self_description or use default
                    occupation = 'Merchant'

                # Safely get personality
                personality = getattr(agent.scratch, 'personality', {})
                if isinstance(personality, dict):
                    personality_data = {
                        'extraversion': personality.get('extraversion', 0),
                        'agreeableness': personality.get('agreeableness', 0),
                        'conscientiousness': personality.get('conscientiousness', 0),
                        'neuroticism': personality.get('neuroticism', 0),
                        'openness': personality.get('openness', 0)
                    }
                else:
                    personality_data = {
                        'extraversion': 0,
                        'agreeableness': 0,
                        'conscientiousness': 0,
                        'neuroticism': 0,
                        'openness': 0
                    }

                agents_data.append({
                    'id': agent_id,
                    'name': agent.scratch.get_fullname(),
                    'age': getattr(agent.scratch, 'age', 0),
                    'occupation': occupation,
                    'address': getattr(agent.scratch, 'living_area', 'Unknown'),
                    'personality': personality_data,
                    'self_description': getattr(agent.scratch, 'self_description', ''),
                    'inventory_count': len(agent.inventory.items) if hasattr(agent, 'inventory') else 0
                })
            except Exception as e:
                print(f"Error loading agent {agent_id}: {e}")
                import traceback
                traceback.print_exc()
                continue

    return jsonify({'agents': agents_data, 'population': population})


@app.route('/api/agent/<agent_id>', methods=['GET'])
def get_agent_details(agent_id):
    """Get detailed information for a specific agent."""
    population = request.args.get('population', 'Synthetic')

    try:
        agent = GenerativeAgent(population, agent_id)

        # Get inventory details
        inventory = []
        if hasattr(agent, 'inventory'):
            for item_name, item_data in agent.inventory.items.items():
                inventory.append({
                    'name': item_name,
                    'quantity': item_data.get('quantity', 0),
                    'base_value': item_data.get('base_value', 0),
                    'cost_value': item_data.get('cost_value', 0),
                    'description': item_data.get('description', '')
                })

        # Get recent memories
        recent_memories = []
        if hasattr(agent, 'memory_stream') and hasattr(agent.memory_stream, 'nodes'):
            sorted_nodes = sorted(
                agent.memory_stream.nodes.items(),
                key=lambda x: x[1].get('created', 0),
                reverse=True
            )
            for node_id, node_data in sorted_nodes[:5]:
                recent_memories.append({
                    'text': node_data.get('description', ''),
                    'created': node_data.get('created', 0),
                    'importance': node_data.get('importance', 0)
                })

        # Safely get occupation
        occupation = getattr(agent.scratch, 'occupation', None)
        if not occupation:
            occupation = 'Merchant'

        # Safely get personality
        personality = getattr(agent.scratch, 'personality', {})
        if isinstance(personality, dict):
            personality_data = {
                'extraversion': personality.get('extraversion', 0),
                'agreeableness': personality.get('agreeableness', 0),
                'conscientiousness': personality.get('conscientiousness', 0),
                'neuroticism': personality.get('neuroticism', 0),
                'openness': personality.get('openness', 0)
            }
        else:
            personality_data = {
                'extraversion': 0,
                'agreeableness': 0,
                'conscientiousness': 0,
                'neuroticism': 0,
                'openness': 0
            }

        return jsonify({
            'id': agent_id,
            'name': agent.scratch.get_fullname(),
            'age': getattr(agent.scratch, 'age', 0),
            'occupation': occupation,
            'address': getattr(agent.scratch, 'living_area', 'Unknown'),
            'education': getattr(agent.scratch, 'education', ''),
            'personality': personality_data,
            'self_description': getattr(agent.scratch, 'self_description', ''),
            'inventory': inventory,
            'recent_memories': recent_memories
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start a new simulation."""
    global simulation_thread, simulation_running, markov_chain, simulation_agents, simulation_config

    if simulation_running:
        return jsonify({'error': 'Simulation already running'}), 400

    data = request.json
    agent_ids = data.get('agents', [])
    num_steps = data.get('num_steps', 20)
    context = data.get('context', 'Marketplace')
    self_reflection_prob = data.get('self_reflection_prob', 0.3)
    interaction_prob = data.get('interaction_prob', 0.7)
    max_turns = data.get('max_turns', 6)

    if len(agent_ids) < 2:
        return jsonify({'error': 'Need at least 2 agents'}), 400

    # Initialize new chain
    markov_chain = MarkovAgentChain(event_queue_maxlen=2000)
    simulation_agents = agent_ids
    simulation_config = {
        'num_steps': num_steps,
        'context': context,
        'self_reflection_prob': self_reflection_prob,
        'interaction_prob': interaction_prob,
        'max_turns': max_turns
    }

    # Start simulation in background
    simulation_running = True
    simulation_thread = threading.Thread(
        target=run_simulation_background,
        args=(agent_ids, num_steps, context, self_reflection_prob, interaction_prob, max_turns)
    )
    simulation_thread.start()

    return jsonify({
        'status': 'started',
        'agents': agent_ids,
        'config': simulation_config
    })


@app.route('/api/simulation/status', methods=['GET'])
def get_simulation_status():
    """Get current simulation status."""
    return jsonify({
        'running': simulation_running,
        'agents': simulation_agents,
        'config': simulation_config
    })


@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the running simulation."""
    global simulation_running

    if not simulation_running:
        return jsonify({'error': 'No simulation running'}), 400

    simulation_running = False
    return jsonify({'status': 'stopping'})


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get new events from the queue."""
    global markov_chain

    if markov_chain is None:
        return jsonify({'events': []})

    count = request.args.get('count', type=int)
    events = markov_chain.get_events(count=count)

    return jsonify({'events': events, 'count': len(events)})


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get current agent leaderboard."""
    global markov_chain

    if markov_chain is None:
        return jsonify({'leaderboard': []})

    leaderboard = markov_chain.get_leaderboard()
    return jsonify({'leaderboard': leaderboard})


@app.route('/api/network', methods=['GET'])
def get_network():
    """Get network graph data."""
    global markov_chain, simulation_agents_loaded, simulation_transition_matrix

    if markov_chain is None or not simulation_agents_loaded:
        return jsonify({'network': {'nodes': [], 'edges': []}})

    # Use already-loaded agents instead of reloading
    try:
        # Use cached transition matrix if available, otherwise create it
        if simulation_transition_matrix is not None:
            import numpy as np
            transition_matrix = np.array(simulation_transition_matrix)
        else:
            transition_matrix = markov_chain.create_agent_transition_matrix(
                len(simulation_agents_loaded),
                simulation_config.get('self_reflection_prob', 0.3),
                simulation_config.get('interaction_prob', 0.7)
            )

        network_data = markov_chain.get_network_data(simulation_agents_loaded, transition_matrix)
        return jsonify({'network': network_data})
    except Exception as e:
        print(f"Error getting network data: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({'network': {'nodes': [], 'edges': []}})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)