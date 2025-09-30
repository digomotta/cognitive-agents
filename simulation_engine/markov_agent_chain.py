"""
Markov Chain Agent Interaction System

In this system:
- Each agent is a state in the Markov chain
- State transition i→i: Agent i reflects on memories
- State transition i→j: Agents i and j have a 2-agent conversation
- Chain continues: i→j (conversation), j→k (conversation), etc.

This creates a dynamic system where agents interact pairwise based on 
Markov chain probabilities, with reflection when staying in same state.
"""

import numpy as np
import random
import time
from typing import List, Dict, Optional
from collections import deque

from simulation_engine.settings import *
from simulation_engine.global_methods import *
from generative_agent.generative_agent import *
from generative_agent.modules.conversation_trade_analyzer import ConversationTradeAnalyzer
from generative_agent.modules.conversation_interaction import ConversationBasedInteraction


class MarkovAgentChain:
    """Markov chain where each state is an agent, transitions trigger interactions."""

    def __init__(self, event_queue_maxlen: int = 1000):
        self.trade_analyzer = ConversationTradeAnalyzer()
        self.conversation_manager = ConversationBasedInteraction()
        self.interaction_history = []

        # Event queue for frontend consumption
        self.event_queue = deque(maxlen=event_queue_maxlen)

        # Cumulative trade stats for leaderboard
        self.agent_stats = {}  # {agent_name: {sales: 0, purchases: 0, net_value: 0, trade_count: 0}}

    def _emit_event(self, event_type: str, data: Dict):
        """
        Emit an event to the queue for frontend consumption.

        Args:
            event_type: Type of event ('utterance', 'trade', 'reflection', 'network_update')
            data: Event data dictionary
        """
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'data': data
        }
        self.event_queue.append(event)

    def _update_agent_stats(self, trade_result: Dict):
        """
        Update cumulative agent statistics from a trade.

        Args:
            trade_result: Trade result dictionary
        """
        if not trade_result.get('executed'):
            return

        details = trade_result.get('trade_details', {})
        participants = details.get('participants', {})
        items = details.get('items', [])

        seller = participants.get('seller')
        buyer = participants.get('buyer')

        if not seller or not buyer or not items:
            return

        # Calculate total trade value
        total_value = sum(item.get('value', 0) * item.get('quantity', 1) for item in items)

        # Initialize stats if needed
        if seller not in self.agent_stats:
            self.agent_stats[seller] = {'sales': 0, 'purchases': 0, 'net_value': 0, 'trade_count': 0}
        if buyer not in self.agent_stats:
            self.agent_stats[buyer] = {'sales': 0, 'purchases': 0, 'net_value': 0, 'trade_count': 0}

        # Update stats
        self.agent_stats[seller]['sales'] += total_value
        self.agent_stats[seller]['net_value'] += total_value
        self.agent_stats[seller]['trade_count'] += 1

        self.agent_stats[buyer]['purchases'] += total_value
        self.agent_stats[buyer]['net_value'] -= total_value
        self.agent_stats[buyer]['trade_count'] += 1

    def get_events(self, count: Optional[int] = None) -> List[Dict]:
        """
        Get events from the queue.

        Args:
            count: Number of events to retrieve (None = all)

        Returns:
            List of events
        """
        if count is None:
            events = list(self.event_queue)
            self.event_queue.clear()
            return events
        else:
            events = []
            for _ in range(min(count, len(self.event_queue))):
                events.append(self.event_queue.popleft())
            return events

    def get_leaderboard(self) -> List[Dict]:
        """
        Get agent leaderboard sorted by sales.

        Returns:
            List of agent stats sorted by sales (descending)
        """
        leaderboard = []
        for agent_name, stats in self.agent_stats.items():
            leaderboard.append({
                'agent': agent_name,
                **stats
            })
        return sorted(leaderboard, key=lambda x: x['sales'], reverse=True)

    def get_network_data(self, agents: List[GenerativeAgent], transition_matrix: np.ndarray) -> Dict:
        """
        Get network graph data with agents as nodes and transition probabilities as edges.

        Args:
            agents: List of agents
            transition_matrix: Transition probability matrix

        Returns:
            Dict with nodes and edges for network visualization
        """
        nodes = []
        for i, agent in enumerate(agents):
            agent_name = agent.scratch.get_fullname()
            stats = self.agent_stats.get(agent_name, {'sales': 0, 'purchases': 0, 'net_value': 0, 'trade_count': 0})
            nodes.append({
                'id': agent_name,
                'index': i,
                'sales': stats['sales'],
                'purchases': stats['purchases'],
                'net_value': stats['net_value'],
                'trade_count': stats['trade_count']
            })

        edges = []
        for i in range(len(agents)):
            for j in range(len(agents)):
                if i != j and transition_matrix[i][j] > 0:
                    edges.append({
                        'source': agents[i].scratch.get_fullname(),
                        'target': agents[j].scratch.get_fullname(),
                        'weight': float(transition_matrix[i][j])
                    })

        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def create_agent_transition_matrix(self, num_agents: int, 
                                     self_reflection_probability: float = 0.3,
                                     interaction_probability: float = 0.7) -> np.ndarray:
        """
        Create transition matrix where each state represents an agent.
        
        Args:
            num_agents: Number of agents (states) in the chain
            self_reflection_probability: Probability of staying in same state (reflection)
            interaction_probability: Probability of transitioning to other agents
            
        Returns:
            np.ndarray: Transition matrix where matrix[i][j] = P(agent_i → agent_j)
        """
        matrix = np.zeros((num_agents, num_agents))
        
        for i in range(num_agents):
            # Probability of staying in same state (self-reflection)
            matrix[i][i] = self_reflection_probability
            
            # Distribute interaction probability among other agents
            if num_agents > 1:
                other_prob = interaction_probability / (num_agents - 1)
                for j in range(num_agents):
                    if i != j:
                        matrix[i][j] = other_prob
        
        # Normalize rows to ensure probabilities sum to 1
        for i in range(num_agents):
            row_sum = np.sum(matrix[i])
            if row_sum > 0:
                matrix[i] = matrix[i] / row_sum
        
        return matrix
    
    def select_next_agent_state(self, current_state: int, transition_matrix: np.ndarray) -> int:
        """
        Select next agent state based on Markov transition probabilities.
        
        Args:
            current_state: Current agent index (state)
            transition_matrix: Transition probability matrix
            
        Returns:
            int: Next agent index (state)
        """
        probabilities = transition_matrix[current_state]
        return np.random.choice(len(probabilities), p=probabilities)
    
    def agent_self_reflection(self, agent: GenerativeAgent, context: str, step: int, testing_mode: bool = True):
        """
        Handle agent self-reflection when staying in same state.

        Args:
            agent: Agent to reflect
            context: Overall simulation context
            step: Current step in the chain
        """
        print(f"Step {step}: {agent.scratch.get_fullname()} stays in current state → REFLECTS")

        # Create reflection anchor based on recent interactions
        reflection_anchor = f"recent interactions and experiences in {context}"
        if self.interaction_history:
            last_interaction = self.interaction_history[-1]
            if last_interaction['type'] == 'conversation' and agent.scratch.get_fullname() in last_interaction['participants']:
                reflection_anchor = f"recent conversation about {last_interaction['context']}"

        # Trigger reflection
        reflections = []
        try:
            reflections = agent.memory_stream.reflect(reflection_anchor, reflection_count=3, retrieval_count=5, time_step=step)
            if not testing_mode:
                agent.save()  # Only save to persist reflections if not in testing mode
                print(f"   → Reflected on: {reflection_anchor} (saved to JSON)")
            else:
                print(f"   → Reflected on: {reflection_anchor} (testing mode - not saved)")

            # Print reflections
            if reflections:
                print(f"   → Reflections:")
                for i, r in enumerate(reflections, 1):
                    print(f"      {i}. {r}")
        except Exception as e:
            print(f"   → Reflection failed: {e}")
            # Try simpler reflection
            try:
                simple_thought = f"I reflected on {reflection_anchor} at step {step}"
                agent.remember(simple_thought)
                reflections = [simple_thought]
                if not testing_mode:
                    agent.save()  # Only save the simple memory if not in testing mode
                    print(f"   → Added simple reflection memory instead (saved to JSON)")
                else:
                    print(f"   → Added simple reflection memory instead (testing mode - not saved)")
            except Exception as e2:
                print(f"   → Both reflection methods failed: {e2}")
                reflections = []

        # Emit reflection event with thoughts
        self._emit_event('reflection', {
            'markov_step': step,
            'agent': agent.scratch.get_fullname(),
            'anchor': reflection_anchor,
            'context': context,
            'thoughts': reflections if reflections else ['Reflection in progress...']
        })

        # Record reflection in history
        self.interaction_history.append({
            'type': 'reflection',
            'step': step,
            'agent': agent.scratch.get_fullname(),
            'anchor': reflection_anchor
        })
    
    def two_agent_conversation(self, agent1: GenerativeAgent, agent2: GenerativeAgent, 
                             context: str, step: int, max_turns: int = 8, 
                             testing_mode: bool = True) -> Dict:
        """
        Conduct conversation between two agents.
        
        Args:
            agent1: First agent
            agent2: Second agent  
            context: Conversation context
            step: Current step in Markov chain
            max_turns: Maximum conversation turns
            testing_mode: Whether to save changes
            
        Returns:
            Dict: Conversation results
        """
        conversation_id = f"markov_step_{step}_{agent1.scratch.get_fullname()}_{agent2.scratch.get_fullname()}_{int(time.time())}"
        
        print(f"Step {step}: {agent1.scratch.get_fullname()} → {agent2.scratch.get_fullname()} → CONVERSATION")
        print(f"   Context: {context}")
        
        # Show initial inventories
        print(f"   {agent1.scratch.get_fullname()}: {agent1.get_all_items_with_values()}")
        print(f"   {agent2.scratch.get_fullname()}: {agent2.get_all_items_with_values()}")
        
        # Initialize conversation
        curr_dialogue = []
        trades_executed = []
        conversation_ended = False
        current_speaker = agent1  # Start with first agent
        other_agent = agent2
        
        # Conversation loop
        for turn in range(max_turns):
            try:
                # Current agent speaks
                response, sales_detected, ended = current_speaker.Act(
                    conversation_id, curr_dialogue, context, turn
                )
                curr_dialogue.append([current_speaker.scratch.get_fullname(), response])
                print(f"   {current_speaker.scratch.get_fullname()}: {response}")

                # Emit utterance event
                self._emit_event('utterance', {
                    'markov_step': step,
                    'conversation_turn': turn,
                    'conversation_id': conversation_id,
                    'agent': current_speaker.scratch.get_fullname(),
                    'text': response,
                    'participants': [agent1.scratch.get_fullname(), agent2.scratch.get_fullname()],
                    'context': context,
                    'ended': ended
                })

                # Check for conversation end
                if ended:
                    print(f"   → Conversation ended by {current_speaker.scratch.get_fullname()}")
                    conversation_ended = True
                    break

                # Handle trade detection
                if sales_detected:
                    print(f"   → Sales detected at turn {turn}")
                    trade_result = self.trade_analyzer.execute_trade(
                        agents=[agent1, agent2],
                        conversation_id=conversation_id,
                        conversation_text=curr_dialogue,
                        context=context,
                        time_step=turn,
                        testing_mode=testing_mode
                    )
                    if trade_result:
                        trades_executed.append(trade_result)
                        if trade_result.get('executed'):
                            print(f"   → Trade executed: {trade_result['trade_details']}")

                            # Update agent stats and emit trade event
                            self._update_agent_stats(trade_result)
                            self._emit_event('trade', {
                                'markov_step': step,
                                'conversation_turn': turn,
                                'conversation_id': conversation_id,
                                'trade_details': trade_result['trade_details'],
                                'participants': [agent1.scratch.get_fullname(), agent2.scratch.get_fullname()],
                                'context': context
                            })
                        else:
                            warning_msg = trade_result.get('warning')
                            if warning_msg:
                                print(f"   → {warning_msg}")
                                # Add warning to conversation so agents are aware
                                curr_dialogue.append(["[System]", warning_msg])
                                # Update both agents' working memory with the warning
                                agent1.working_memory.add_conversation_turn("[System]", warning_msg)
                                agent2.working_memory.add_conversation_turn("[System]", warning_msg)
                            else:
                                print(f"   → Trade detected but not executed")

                # Switch speakers
                current_speaker, other_agent = other_agent, current_speaker

            except Exception as e:
                print(f"   → Error in conversation: {e}")
                break
        
        # End conversation handling
        self.conversation_manager.end_conversation(
            agents=[agent1, agent2],
            conversation_id=conversation_id,
            time_step=turn if 'turn' in locals() else max_turns - 1,
            testing_mode=testing_mode
        )
        
        # Show final inventories
        print(f"   Final {agent1.scratch.get_fullname()}: {agent1.get_all_items_with_values()}")
        print(f"   Final {agent2.scratch.get_fullname()}: {agent2.get_all_items_with_values()}")
        
        # Record interaction in history
        interaction_result = {
            'type': 'conversation',
            'step': step,
            'participants': [agent1.scratch.get_fullname(), agent2.scratch.get_fullname()],
            'context': context,
            'dialogue': curr_dialogue,
            'trades': trades_executed,
            'turns': len(curr_dialogue),
            'ended_naturally': conversation_ended
        }
        self.interaction_history.append(interaction_result)
        
        return interaction_result
    
    def run_markov_chain(self, agents: List[GenerativeAgent], 
                        context: str = "Marketplace",
                        num_steps: int = 20,
                        self_reflection_prob: float = 0.3,
                        interaction_prob: float = 0.7,
                        transition_matrix: Optional[np.ndarray] = None,
                        conversation_max_turns: int = 8,
                        start_agent: Optional[int] = None,
                        testing_mode: bool = True) -> Dict:
        """
        Run the Markov chain simulation with agents as states.
        
        Args:
            agents: List of GenerativeAgent objects
            context: Overall simulation context
            num_steps: Number of Markov chain steps
            self_reflection_prob: Probability of staying in same state (reflection)
            interaction_prob: Probability of transitioning to other states
            transition_matrix: Custom transition matrix (optional)
            conversation_max_turns: Max turns per 2-agent conversation
            testing_mode: Whether to save agent changes
            
        Returns:
            Dict: Complete simulation results
        """
        if len(agents) < 2:
            raise ValueError("Need at least 2 agents for Markov chain")
        
        print(f"=== Markov Agent Chain Simulation ===")
        print(f"Agents (States): {[agent.scratch.get_fullname() for agent in agents]}")
        print(f"Steps: {num_steps}")
        
        if transition_matrix is None:
            print(f"Self-reflection probability: {self_reflection_prob}")
            print(f"Interaction probability: {interaction_prob}")

        print(f"Context: {context}")
        print()
        
        # Create or use transition matrix
        if transition_matrix is None:
            transition_matrix = self.create_agent_transition_matrix(
                len(agents), self_reflection_prob, interaction_prob
            )
        
        print("Transition Matrix (Agent States):")
        agent_names = [agent.scratch.get_fullname() for agent in agents]
        print("     ", "  ".join([f"{name[:8]:<8}" for name in agent_names]))
        for i, row in enumerate(transition_matrix):
            print(f"{agent_names[i][:8]:<8}", "  ".join([f"{prob:.3f}" for prob in row]))
        print()

        # Initialize chain state
        if start_agent is None:
            current_state = random.randint(0, len(agents) - 1)
        else:
            current_state = start_agent

        self.interaction_history = []
        
        # Run Markov chain steps
        for step in range(num_steps):
            current_agent = agents[current_state]

            # Select next state
            next_state = self.select_next_agent_state(current_state, transition_matrix)

            if next_state == current_state:
                # Stay in same state → Reflection
                self.agent_self_reflection(current_agent, context, step + 1, testing_mode)
            else:
                # Transition to different state → Conversation
                next_agent = agents[next_state]
                self.two_agent_conversation(
                    current_agent, next_agent, context, step + 1,
                    conversation_max_turns, testing_mode
                )

            # Emit network update event periodically (every 5 steps)
            if (step + 1) % 5 == 0:
                network_data = self.get_network_data(agents, transition_matrix)
                self._emit_event('network_update', {
                    'markov_step': step + 1,
                    'network': network_data,
                    'leaderboard': self.get_leaderboard()
                })

            # Move to next state
            current_state = next_state
            print()  # Add spacing between steps
        
        # Generate summary
        conversation_count = len([h for h in self.interaction_history if h['type'] == 'conversation'])
        reflection_count = len([h for h in self.interaction_history if h['type'] == 'reflection'])
        
        # Collect all trades from conversations
        all_trades = []
        executed_trades = []
        for interaction in self.interaction_history:
            if interaction['type'] == 'conversation' and 'trades' in interaction:
                all_trades.extend(interaction['trades'])
                executed_trades.extend([t for t in interaction['trades'] if t.get('executed')])
        
        print("=== Simulation Summary ===")
        print(f"Total conversations: {conversation_count}")
        print(f"Total reflections: {reflection_count}")
        print(f"Total trades attempted: {len(all_trades)}")
        print(f"Total trades executed: {len(executed_trades)}")
        if executed_trades:
            print("Executed trades:")
            for i, trade in enumerate(executed_trades, 1):
                details = trade.get('trade_details', {})
                participants = details.get('participants', {})
                items = details.get('items', [])
                if participants and items:
                    seller = participants.get('seller', 'Unknown')
                    buyer = participants.get('buyer', 'Unknown')
                    item_summary = ', '.join([f"{item['quantity']} {item['name']} (${item['value']})" for item in items])
                    print(f"  {i}. {seller} → {buyer}: {item_summary}")
        print(f"Final state: {agents[current_state].scratch.get_fullname()}")
        
        return {
            'agents': [agent.scratch.get_fullname() for agent in agents],
            'transition_matrix': transition_matrix.tolist() if hasattr(transition_matrix, 'tolist') else transition_matrix,
            'interaction_history': self.interaction_history,
            'conversation_count': conversation_count,
            'reflection_count': reflection_count,
            'total_trades_attempted': len(all_trades),
            'total_trades_executed': len(executed_trades),
            'all_trades': all_trades,
            'executed_trades': executed_trades,
            'final_state': current_state,
            'final_agent': agents[current_state].scratch.get_fullname()
        }


def load_agents_for_chain(population: str, agent_names: List[str]) -> List[GenerativeAgent]:
    """Load agents for Markov chain simulation."""
    agents = []
    for name in agent_names:
        try:
            agent = GenerativeAgent(population, name)
            agents.append(agent)
            print(f"Loaded: {agent.scratch.get_fullname()}")
        except Exception as e:
            print(f"Failed to load {name}: {e}")
    return agents


def test_markov_agent_chain():
    """Test the Markov agent chain system."""
    print("=== Testing Markov Agent Chain ===")
    
    # Load agents
    agent_names = ["rowan_greenwood", "jasmine_carter"]
    agents = load_agents_for_chain("Synthetic", agent_names)
    
    if len(agents) < 2:
        print("Need at least 2 agents to test")
        return
    
    # Create and run chain
    chain = MarkovAgentChain()
    
    results = chain.run_markov_chain(
        agents=agents,
        context="Local community market interactions",
        num_steps=15,
        self_reflection_prob=0.4,
        interaction_prob=0.6,
        conversation_max_turns=6,
        testing_mode=True
    )
    
    print("\n=== Results Analysis ===")
    print(f"Conversation-to-reflection ratio: {results['conversation_count']}:{results['reflection_count']}")
    
    return results


if __name__ == '__main__':
    test_markov_agent_chain()