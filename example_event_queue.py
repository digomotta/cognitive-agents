"""
Example: Using the Event Queue System

This demonstrates how to access events from MarkovAgentChain for frontend consumption.
"""

from markov_agent_chain import MarkovAgentChain, load_agents_for_chain


def run_simulation_with_events():
    """Run simulation and demonstrate event queue access."""

    # Load agents
    agent_names = ["rowan_greenwood", "jasmine_carter", "carlos_mendez"]
    agents = load_agents_for_chain("Synthetic", agent_names)

    if len(agents) < 2:
        print("Need at least 2 agents")
        return

    # Create chain
    chain = MarkovAgentChain(event_queue_maxlen=1000)

    print("=== Starting Simulation ===\n")

    # Run simulation (this will populate the event queue)
    results = chain.run_markov_chain(
        agents=agents,
        context="Local market interactions",
        num_steps=10,
        self_reflection_prob=0.3,
        interaction_prob=0.7,
        conversation_max_turns=4,
        testing_mode=True
    )

    print("\n\n=== Event Queue Analysis ===\n")

    # Get all events from the queue
    events = chain.get_events()

    print(f"Total events captured: {len(events)}\n")

    # Count events by type
    event_types = {}
    for event in events:
        event_type = event['type']
        event_types[event_type] = event_types.get(event_type, 0) + 1

    print("Events by type:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")

    print("\n=== Sample Events ===\n")

    # Show utterances
    utterances = [e for e in events if e['type'] == 'utterance']
    if utterances:
        print(f"Sample Utterances (showing first 3 of {len(utterances)}):")
        for i, event in enumerate(utterances[:3]):
            data = event['data']
            print(f"\n  {i+1}. Markov Step {data['markov_step']}, Conversation Turn {data['conversation_turn']}")
            print(f"     {data['agent']}: {data['text'][:100]}...")
            print(f"     Context: {data['context']}")

    # Show trades
    trades = [e for e in events if e['type'] == 'trade']
    if trades:
        print(f"\n\nTrades Executed (showing all {len(trades)}):")
        for i, event in enumerate(trades):
            data = event['data']
            details = data['trade_details']
            participants = details.get('participants', {})
            items = details.get('items', [])
            print(f"\n  {i+1}. Markov Step {data['markov_step']}, Conversation Turn {data['conversation_turn']}")
            print(f"     {participants.get('seller')} → {participants.get('buyer')}")
            for item in items:
                print(f"     - {item['quantity']} {item['name']} @ ${item['value']}")
            print(f"     Context: {data['context']}")

    # Show reflections
    reflections = [e for e in events if e['type'] == 'reflection']
    if reflections:
        print(f"\n\nReflections (showing all {len(reflections)}):")
        for i, event in enumerate(reflections):
            data = event['data']
            print(f"\n  {i+1}. Markov Step {data['markov_step']}: {data['agent']}")
            print(f"     Anchor: {data['anchor']}")
            print(f"     Context: {data['context']}")

    # Show network updates
    network_updates = [e for e in events if e['type'] == 'network_update']
    if network_updates:
        print(f"\n\nNetwork Updates: {len(network_updates)}")
        last_network = network_updates[-1]['data']['network']
        print(f"  Nodes: {len(last_network['nodes'])}")
        print(f"  Edges: {len(last_network['edges'])}")

    print("\n\n=== Leaderboard ===\n")

    # Get leaderboard
    leaderboard = chain.get_leaderboard()
    for i, entry in enumerate(leaderboard):
        print(f"{i+1}. {entry['agent']}")
        print(f"   Sales: ${entry['sales']:.2f}")
        print(f"   Purchases: ${entry['purchases']:.2f}")
        print(f"   Net Value: ${entry['net_value']:.2f}")
        print(f"   Trades: {entry['trade_count']}")
        print()

    return chain, events, leaderboard


def simulate_frontend_polling(chain, num_steps=10):
    """
    Simulate how a frontend would poll for new events.
    This runs the simulation step-by-step and polls events after each step.
    """
    print("\n=== Simulating Frontend Polling ===\n")

    # This is a simplified example - in reality you'd run the simulation
    # in a background thread and poll from your frontend

    print("In a real frontend, you would:")
    print("1. Start simulation in background thread")
    print("2. Poll GET /api/events endpoint every 1-2 seconds")
    print("3. Display new utterances in chat feed")
    print("4. Update leaderboard when trades occur")
    print("5. Refresh network graph every 5-10 steps")
    print("\nSample API endpoints needed:")
    print("  GET  /api/events          - Get new events from queue")
    print("  GET  /api/leaderboard     - Get current leaderboard")
    print("  GET  /api/network         - Get network graph data")
    print("  POST /api/start           - Start simulation")
    print("  POST /api/stop            - Stop simulation")


if __name__ == '__main__':
    chain, events, leaderboard = run_simulation_with_events()
    simulate_frontend_polling(chain)