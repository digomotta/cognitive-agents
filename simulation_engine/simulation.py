from typing import Dict, List, Any
import json
import os
import numpy as np
from datetime import datetime
from simulation_engine.markov_agent_chain import MarkovAgentChain, load_agents_for_chain
from .settings import DEBUG
import random


class Simulation:
    """Manages the full agent simulation with production cycles and network weight calculation."""

    def __init__(self, population: str = "Synthetic", agent_names: List[str] = None):
        """Initialize simulation with agents."""
        if agent_names is None:
            agent_names = ["rowan_greenwood", "jasmine_carter", "mina_kim", "kemi_adebayo",
                          "bianca_silva", "mei_chen", "carlos_mendez", "pema_sherpa"]

        self.population = population
        self.agent_names = agent_names
        self.agents = []
        self.network_weights = {}
        self.network_weights_history = []  # Store weights at each cycle
        self.transition_matrices_history = []  # Store transition matrices at each weight cycle
        self.markov_chain = MarkovAgentChain()
        self.current_time_step = 0
        self.cycle_count = 0

        # Create output directory
        self.output_dir = "output"
        self.create_output_directory()

    def load_agents(self) -> bool:
        """Load all agents for the simulation."""
        print("Loading agents for simulation...")
        self.agents = load_agents_for_chain(self.population, self.agent_names)

        if len(self.agents) < 2:
            print("Error: Could not load required agents")
            return False

        print(f"Successfully loaded {len(self.agents)} agents")
        return True

    def create_output_directory(self):
        """Create output directory for saving cycle results."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

    def save_cycle_results(self, cycle_results: Dict[str, Any], production_results: Dict[str, Any],
                          network_weights: Dict[str, Dict[str, float]], transition_matrix: 'np.ndarray' = None):
        """Save cycle results to JSON files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save cycle simulation results
        cycle_filename = f"{self.output_dir}/cycle_{self.cycle_count:03d}_{timestamp}_simulation.json"
        cycle_data = {
            "cycle": self.cycle_count,
            "time_step": self.current_time_step,
            "timestamp": timestamp,
            "results": cycle_results
        }

        with open(cycle_filename, 'w') as f:
            json.dump(cycle_data, f, indent=2, default=str)

        if DEBUG:
            print(f"  Saved cycle simulation results: {cycle_filename}")

        # Save production results (if any)
        production_filename = None
        if production_results is not None:
            production_filename = f"{self.output_dir}/cycle_{self.cycle_count:03d}_{timestamp}_production.json"
            production_data = {
                "cycle": self.cycle_count,
                "time_step": self.current_time_step,
                "timestamp": timestamp,
                "production_results": production_results
            }

            with open(production_filename, 'w') as f:
                json.dump(production_data, f, indent=2, default=str)

            if DEBUG:
                print(f"  Saved production results: {production_filename}")

        # Save network weights and transition matrix
        weights_filename = f"{self.output_dir}/cycle_{self.cycle_count:03d}_{timestamp}_weights.json"
        weights_data = {
            "cycle": self.cycle_count,
            "time_step": self.current_time_step,
            "timestamp": timestamp,
            "network_weights": network_weights,
            "transition_matrix": transition_matrix.tolist() if transition_matrix is not None else None,
            "agent_names": [agent.scratch.get_fullname() for agent in self.agents]
        }

        with open(weights_filename, 'w') as f:
            json.dump(weights_data, f, indent=2, default=str)

        if DEBUG:
            print(f"  Saved network weights and transition matrix: {weights_filename}")

        print(f"Saved cycle {self.cycle_count} outputs to {self.output_dir}/")
        return {
            "cycle_file": cycle_filename,
            "production_file": production_filename,
            "weights_file": weights_filename
        }

    def calculate_network_weights(self) -> Dict[str, Dict[str, float]]:
        """Calculate network weights using Markov buying interest scores."""
        print("Calculating network weights...")
        self.network_weights = {}
        agent_names = [agent.scratch.get_fullname() for agent in self.agents]

        for agent in self.agents:
            agent_name = agent.scratch.get_fullname()
            other_agents = [name for name in agent_names if name != agent_name]

            if other_agents:
                try:
                    weights = agent.get_markov_buying_interest_scores(other_agents, temperature=12.0)
                    self.network_weights[agent_name] = weights
                    if DEBUG:
                        print(f"  {agent_name}: calculated weights for {len(weights)} connections")
                except Exception as e:
                    print(f"Error calculating weights for {agent_name}: {e}")
                    # Default to uniform weights if calculation fails
                    uniform_weight = 1.0 / len(other_agents) if other_agents else 0.0
                    self.network_weights[agent_name] = {name: uniform_weight for name in other_agents}

        # Save weights to history with cycle info
        weights_snapshot = {
            'cycle': self.cycle_count,
            'time_step': self.current_time_step,
            'weights': self.network_weights.copy(),
            'type': 'updated_from_trading'
        }
        self.network_weights_history.append(weights_snapshot)

        # Create and save transition matrix from new weights
        transition_matrix = self.create_transition_matrix_from_weights(self_reflection_prob=0.2)
        matrix_snapshot = {
            'cycle': self.cycle_count,
            'time_step': self.current_time_step,
            'transition_matrix': transition_matrix.tolist(),
            'agent_names': [agent.scratch.get_fullname() for agent in self.agents],
            'type': 'updated_from_trading'
        }
        self.transition_matrices_history.append(matrix_snapshot)

        return self.network_weights

    def initialize_uniform_weights(self):
        """Initialize network weights with uniform distribution for all agents."""
        print("Initializing uniform network weights...")
        self.network_weights = {}
        agent_names = [agent.scratch.get_fullname() for agent in self.agents]

        for agent in self.agents:
            agent_name = agent.scratch.get_fullname()
            other_agents = [name for name in agent_names if name != agent_name]

            if other_agents:
                # Set uniform weights for all other agents
                uniform_weight = 1.0 / len(other_agents)
                self.network_weights[agent_name] = {name: uniform_weight for name in other_agents}
                print(f"  {agent_name}: uniform weights ({uniform_weight:.3f}) for {len(other_agents)} connections")

        # Save initial uniform weights to history
        weights_snapshot = {
            'cycle': 0,
            'time_step': 0,
            'weights': self.network_weights.copy(),
            'type': 'uniform_initial'
        }
        self.network_weights_history.append(weights_snapshot)

        # Create and save initial uniform transition matrix
        transition_matrix = self.create_transition_matrix_from_weights(self_reflection_prob=0.2)
        matrix_snapshot = {
            'cycle': 0,
            'time_step': 0,
            'transition_matrix': transition_matrix.tolist(),
            'agent_names': agent_names,
            'type': 'uniform_initial'
        }
        self.transition_matrices_history.append(matrix_snapshot)

        return self.network_weights

    def create_transition_matrix_from_weights(self, self_reflection_prob: float = 0.2) -> 'np.ndarray':
        """Create transition matrix using current network weights."""
        import numpy as np

        num_agents = len(self.agents)
        matrix = np.zeros((num_agents, num_agents))
        agent_names = [agent.scratch.get_fullname() for agent in self.agents]

        for i, agent_name in enumerate(agent_names):
            # Set self-reflection probability
            matrix[i][i] = self_reflection_prob

            # Get this agent's network weights
            agent_weights = self.network_weights.get(agent_name, {})

            if agent_weights:
                # Use network weights to determine interaction probabilities
                total_weight = sum(agent_weights.values())
                interaction_prob = 1.0 - self_reflection_prob

                for j, other_agent_name in enumerate(agent_names):
                    if i != j:  # Not self
                        if total_weight > 0:
                            # Scale network weight by interaction probability
                            weight = agent_weights.get(other_agent_name, 0.0)
                            matrix[i][j] = (weight / total_weight) * interaction_prob
                        else:
                            # Fallback to uniform if no weights
                            matrix[i][j] = interaction_prob / (num_agents - 1)
            else:
                # Fallback to uniform distribution if no network weights
                interaction_prob = 1.0 - self_reflection_prob
                for j in range(num_agents):
                    if i != j:
                        matrix[i][j] = interaction_prob / (num_agents - 1)

        # Normalize rows to ensure probabilities sum to 1
        for i in range(num_agents):
            row_sum = np.sum(matrix[i])
            if row_sum > 0:
                matrix[i] = matrix[i] / row_sum

        return matrix

    def run_production_phase(self, time_step: int) -> Dict[str, Any]:
        """Run production planning and execution for all agents."""
        print("Running production phase for all agents...")

        # Use the Plan class method to handle all agents
        from generative_agent.modules.cognitive.plan import Plan
        plan_module = Plan()
        production_results = plan_module.execute_production_for_all_agents(self.agents, time_step)

        print(f"Production phase completed for {len(self.agents)} agents")
        return production_results


    def save_all_agents(self):
        """Save all agent states to persist changes."""
        print("Saving agent states...")
        for agent in self.agents:
            agent.save()
        print(f"Saved {len(self.agents)} agent states")

    def run_full_simulation(self, total_steps: int = 120,
                           weight_update_cycle: int = 20, production_cycle: int = 30,
                           testing_mode: bool = False) -> Dict[str, Any]:
        """
        Run the complete simulation with separate cycles for network weights and production.

        Parameters:
            total_steps: Total number of simulation steps
            weight_update_cycle: Number of steps between network weight updates
            production_cycle: Number of steps between production phases
            testing_mode: Whether to run in testing mode
        """
        print("=== Starting Full Agent Simulation ===")

        # Load agents
        if not self.load_agents():
            return None

        # Initialize with uniform network weights for first interaction
        print("=== Phase 1: Initialize Uniform Network Weights ===")
        self.initialize_uniform_weights()
        print()

        # Run simulation step by step with separate weight and production cycles
        all_production_results = []
        last_weight_update = 0
        last_production_update = 0
        current_agent = None

        # Accumulate interactions for the current cycle
        cycle_accumulated_interactions = []
        cycle_accumulated_trades = []
        cycle_start_step = 1

        for step in range(1, total_steps + 1):
            self.current_time_step = step
            print(f"=== Step {step} ===")

            # Run single Markov chain step
            # Create dynamic transition matrix from current network weights
            transition_matrix = self.create_transition_matrix_from_weights(self_reflection_prob=0.2)

            # Run single step of Markov chain
            step_results = self.markov_chain.run_markov_chain(
                agents=self.agents,
                context=f"Step {step} - Community market and trading interactions",
                num_steps=1,  # Single step
                self_reflection_prob=0.2,
                interaction_prob=0.8,
                transition_matrix=transition_matrix,
                conversation_max_turns=8,
                start_agent=current_agent,
                testing_mode=testing_mode
            )

            current_agent = step_results['final_state']

            # Accumulate interaction history from this step with corrected step numbers
            for interaction in step_results.get('interaction_history', []):
                # Update step number to reflect actual simulation step
                interaction['step'] = step
                cycle_accumulated_interactions.append(interaction)

            cycle_accumulated_trades.extend(step_results.get('all_trades', []))

            # Check for weight update cycle
            should_update_weights = (step - last_weight_update) >= weight_update_cycle

            # Check for production cycle
            should_run_production = (step - last_production_update) >= production_cycle

            if should_update_weights or should_run_production:
                print(f"=== Step {step}: Update Phase ===")

                # Phase 1: Network weight recalculation (if due)
                updated_weights = None
                if should_update_weights:
                    print("  → Updating network weights")
                    updated_weights = self.calculate_network_weights()
                    last_weight_update = step
                else:
                    updated_weights = self.network_weights

                # Phase 2: Production planning and execution (if due)
                production_results = None
                if should_run_production:
                    print("  → Running production phase")
                    production_results = self.run_production_phase(step)
                    all_production_results.append(production_results)
                    last_production_update = step

                # Phase 3: Save results to JSON files with accumulated interactions
                # Create cycle results with accumulated data
                cycle_results = {
                    'agents': step_results['agents'],
                    'transition_matrix': step_results['transition_matrix'],
                    'interaction_history': cycle_accumulated_interactions,
                    'conversation_count': len([i for i in cycle_accumulated_interactions if i['type'] == 'conversation']),
                    'reflection_count': len([i for i in cycle_accumulated_interactions if i['type'] == 'reflection']),
                    'total_trades_attempted': len(cycle_accumulated_trades),
                    'total_trades_executed': len([t for t in cycle_accumulated_trades if t.get('executed')]),
                    'all_trades': cycle_accumulated_trades,
                    'executed_trades': [t for t in cycle_accumulated_trades if t.get('executed')],
                    'cycle_start_step': cycle_start_step,
                    'cycle_end_step': step,
                    'final_state': step_results['final_state'],
                    'final_agent': step_results['final_agent']
                }

                # Get the latest transition matrix if weights were updated
                latest_matrix = None
                if should_update_weights and self.transition_matrices_history:
                    latest_matrix_data = self.transition_matrices_history[-1]['transition_matrix']
                    latest_matrix = np.array(latest_matrix_data)

                self.save_cycle_results(cycle_results, production_results, updated_weights, latest_matrix)

                # Phase 4: Save agent states
                self.save_all_agents()

                # Reset accumulated data for next cycle
                cycle_accumulated_interactions = []
                cycle_accumulated_trades = []
                cycle_start_step = step + 1

                print()

        print("=== Simulation Complete ===")
        print(f"Total time steps: {self.current_time_step}")
        print(f"Network weights updated {len(self.network_weights_history)} times")
        print(f"Transition matrices saved {len(self.transition_matrices_history)} times")
        print(f"Production phases executed: {len(all_production_results)} times")
        print(f"Weight update cycle: every {weight_update_cycle} steps")
        print(f"Production cycle: every {production_cycle} steps")

        return {
            'total_steps': self.current_time_step,
            'agents': self.agents,
            'final_network_weights': self.network_weights,
            'network_weights_history': self.network_weights_history,
            'transition_matrices_history': self.transition_matrices_history,
            'production_results': all_production_results,
            'weight_update_cycle': weight_update_cycle,
            'production_cycle': production_cycle
        }