from typing import Dict, List, Any, Optional
import json
import os
from simulation_engine.gpt_structure import gpt_request, generate_prompt
from simulation_engine.settings import LLM_VERS, DEBUG

class ProductionPlan:
    def __init__(self, plan_dict: Dict[str, Any]):
        self.item_name = plan_dict["item_name"]
        self.planned_quantity = plan_dict["planned_quantity"]
        self.reasoning = plan_dict.get("reasoning", "")
        self.created = plan_dict.get("created", 0)
        self.time_step = plan_dict.get("time_step", 0)

    def package(self) -> Dict[str, Any]:
        return {
            "item_name": self.item_name,
            "planned_quantity": self.planned_quantity,
            "reasoning": self.reasoning,
            "created": self.created,
            "time_step": self.time_step
        }

class Plan:
    def __init__(self, plans_data: List[Dict[str, Any]] = None):
        self.production_plans: List[ProductionPlan] = []

        if plans_data:
            for plan_data in plans_data:
                plan = ProductionPlan(plan_data)
                self.production_plans.append(plan)

    def create_production_plan_with_llm(self, agent, item_name: str, time_step: int) -> Optional[ProductionPlan]:
        """
        Create a production plan using LLM analysis of inventory history and memories.

        Parameters:
            agent: The GenerativeAgent instance
            item_name: Name of the item to plan for
            time_step: Current time step

        Returns:
            ProductionPlan object or None if planning fails
        """
        #try:
        # Get agent persona information
        persona_info = f"Agent: {agent.scratch.get_fullname()}\n"
        persona_info += f"Age: {agent.scratch.age}\n"
        persona_info += f"Self Description: {agent.scratch.self_description}\n"

        # Get current inventory status for the item
        current_inventory = agent.inventory.get_all_items_with_values().get(item_name, {
            "quantity": 0,
            "value_per_unit": 0.0,
            "production_cost_per_unit": 0.0,
            "total_value": 0.0,
            "total_production_cost": 0.0
        })

        # Get sales history for the item
        sales_history = agent.get_sales_history(item_name)
        if DEBUG:
            print('Sales history: ', sales_history)

        # Get purchase history for the item
        purchase_history = agent.get_purchase_history(item_name)

        # Get relevant memories about the item, production, or sales
        retrieved_memories = agent.memory_stream.retrieve([item_name, "production", "sales", "business"], time_step, n_count=10)

        memories_text = ""
        for query, memories in retrieved_memories.items():
            if memories:
                memories_text += f"\nMemories about {query}:\n"
                memories_text += "\n".join([f"- {mem.content}" for mem in memories])

        # Get financial information
        agent_name = agent.scratch.get_fullname()
        available_cash = agent.get_inventory_quantity("digital cash")
        production_cost_per_unit = current_inventory.get('production_cost_per_unit', 0.0)
        current_quantity = current_inventory.get('quantity', 0)

        # Calculate maximum affordable production
        max_affordable_units = int(available_cash / production_cost_per_unit) if production_cost_per_unit > 0 else 0

        # Summarize sales history briefly
        recent_sales_summary = f"{len(sales_history)} recent sales" if sales_history else "No recent sales"

        # Summarize memories briefly
        memory_summary = "No relevant memories"
        if memories_text:
            memory_lines = memories_text.split('\n')
            relevant_memories = [line.strip('- ') for line in memory_lines if line.strip().startswith('-')][:3]  # Top 3 memories
            if relevant_memories:
                memory_summary = "; ".join(relevant_memories)

        # Create the planning prompt using template
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        template_path = os.path.join(
            project_root,
            "simulation_engine",
            "prompt_template",
            "generative_agent",
            "planning",
            "production_plan_v1.txt"
        )

        prompt_inputs = [
            agent_name,                              # INPUT 0: agent name
            f"{available_cash:.2f}",                 # INPUT 1: available cash
            item_name,                               # INPUT 2: item name
            f"{production_cost_per_unit:.2f}",       # INPUT 3: production cost per unit
            str(current_quantity),                   # INPUT 4: current inventory
            recent_sales_summary,                    # INPUT 5: recent sales
            memory_summary,                          # INPUT 6: relevant memories
            str(max_affordable_units)                # INPUT 7: max affordable units
        ]

        prompt = generate_prompt(prompt_inputs, template_path)
        if DEBUG:
            print('Prompt: ', prompt)

        # Get LLM response
        response = gpt_request(prompt, model=LLM_VERS)
        if DEBUG:
            print('LLM response: ', response)

        # Check if response contains an error
        if response.startswith("GENERATION ERROR"):
            if DEBUG:
                print(f"LLM generation failed: {response}")
            plan_data = {"planned_quantity": 0, "reasoning": f"LLM generation failed: {response}"}
        else:
            # Parse the JSON response
            try:
                plan_data = json.loads(response)
            except json.JSONDecodeError as e:
                if DEBUG:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response: {response}")
                plan_data = {"planned_quantity": 0, "reasoning": f"Failed to parse LLM response: {str(e)}"}

        # Add metadata
        plan_data["item_name"] = item_name
        plan_data["created"] = time_step
        plan_data["time_step"] = time_step

        # Create and store the plan
        plan = ProductionPlan(plan_data)
        self.production_plans.append(plan)

        return plan

        # except Exception as e:
        #     print(f"Error creating production plan for {item_name}: {e}")
        #     print(response)

        #     # Create a fallback plan with no production
        #     fallback_plan = ProductionPlan({
        #         "item_name": item_name,
        #         "planned_quantity": 0,
        #         "reasoning": f"Unable to generate plan due to error: {str(e)}",
        #         "created": time_step,
        #         "time_step": time_step
        #     })
        #     self.production_plans.append(fallback_plan)
        #     return fallback_plan

    def get_latest_plan(self, item_name: str) -> Optional[ProductionPlan]:
        """Get the most recent production plan for an item."""
        item_plans = [p for p in self.production_plans if p.item_name == item_name]
        if item_plans:
            return max(item_plans, key=lambda p: p.time_step)
        return None

    def get_all_plans(self, item_name: str = None) -> List[ProductionPlan]:
        """Get all production plans, optionally filtered by item."""
        if item_name:
            return [p for p in self.production_plans if p.item_name == item_name]
        return self.production_plans.copy()

    def get_total_planned_quantity(self, item_name: str = None) -> int:
        """Get total planned production quantity for all or specific item."""
        if item_name:
            return sum(p.planned_quantity for p in self.production_plans if p.item_name == item_name)
        return sum(p.planned_quantity for p in self.production_plans)

    def clear_old_plans(self, time_step: int, max_age: int = 10):
        """Remove plans older than max_age time steps."""
        cutoff_time = time_step - max_age
        self.production_plans = [p for p in self.production_plans if p.time_step >= cutoff_time]

    def get_plan_summary(self) -> Dict[str, Any]:
        """Get a summary of all current plans."""
        if not self.production_plans:
            return {
                "total_items_planned": 0,
                "total_planned_quantity": 0,
                "items": {}
            }

        items_summary = {}
        for plan in self.production_plans:
            if plan.item_name not in items_summary:
                items_summary[plan.item_name] = {
                    "planned_quantity": 0,
                    "latest_reasoning": ""
                }

            items_summary[plan.item_name]["planned_quantity"] += plan.planned_quantity
            items_summary[plan.item_name]["latest_reasoning"] = plan.reasoning

        return {
            "total_items_planned": len(items_summary),
            "total_planned_quantity": sum(item["planned_quantity"] for item in items_summary.values()),
            "items": items_summary
        }

    def execute_production_plan(self, agent, plan: ProductionPlan, time_step: int = 0) -> bool:
        """
        Execute a specific production plan.

        Parameters:
            agent: The GenerativeAgent instance
            plan: The ProductionPlan to execute
            time_step: Current time step

        Returns:
            bool: True if production was successful, False otherwise
        """
        # Validate the plan
        if not plan or plan.planned_quantity <= 0:
            if DEBUG:
                print(f"No valid production plan provided")
            return False

        # Get current inventory data for production cost
        current_inventory = agent.inventory.get_all_items_with_values().get(plan.item_name, {})
        production_cost_per_unit = current_inventory.get('production_cost_per_unit', 0.0)

        if production_cost_per_unit <= 0:
            if DEBUG:
                print(f"No production cost defined for {plan.item_name}")
            return False

        # Calculate total production cost
        total_cost = plan.planned_quantity * production_cost_per_unit

        # Check if agent has enough cash
        available_cash = agent.get_inventory_quantity("digital cash")
        if available_cash < total_cost:
            if DEBUG:
                print(f"Insufficient funds: need ${total_cost:.2f}, have ${available_cash:.2f}")
            return False

        # Execute production: pay cost and add items
        try:
            # Remove cash for production cost
            success = agent.remove_from_inventory("digital cash", total_cost, time_step,
                                                f"Production cost for {plan.planned_quantity} {plan.item_name}")
            if not success:
                print(f"Failed to deduct production cost of ${total_cost:.2f}")
                return False

            # Add produced items to inventory
            current_value = current_inventory.get('value_per_unit', 0.0)
            agent.add_to_inventory(plan.item_name, plan.planned_quantity, time_step,
                                 current_value, production_cost_per_unit,
                                 f"Produced based on plan: {plan.reasoning[:50]}...")

            print(f"✓ Successfully produced {plan.planned_quantity} {plan.item_name} for ${total_cost:.2f}")

            # Record the successful production in agent's memory
            agent.remember(f"I produced {plan.planned_quantity} units of {plan.item_name} for ${total_cost:.2f}. " +
                          f"Reasoning: {plan.reasoning[:100]}...", time_step)

            return True

        except Exception as e:
            print(f"Error executing production plan: {e}")
            return False

    def get_items_to_produce(self, agent, max_items: int = 5) -> List[str]:
        """
        Get items to produce based on recent sales activity.

        Parameters:
            agent: The GenerativeAgent instance
            max_items: Maximum number of items to return (default 5)

        Returns:
            List of item names from recent sales, up to max_items
        """
        # Get all inventory records
        all_records = agent.inventory.records

        # Filter for sell_item records and get the last ones
        sell_records = [record for record in all_records if record.action == "sell_item"]

        # Get the last max_items sell records (or all if less than max_items)
        recent_sales = sell_records[-max_items:] if len(sell_records) >= max_items else sell_records

        # Extract unique item names from recent sales, preserving order of most recent
        items_to_produce = []
        for record in reversed(recent_sales):  # Start from most recent
            if record.item_name not in items_to_produce:
                items_to_produce.append(record.item_name)

        return items_to_produce

    def create_production_plans_for_recent_sales(self, agent, time_step: int = 0, max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Create production plans for items based on recent sales activity.

        Parameters:
            agent: The GenerativeAgent instance
            time_step: Current time step
            max_items: Maximum number of items to plan for

        Returns:
            List of production plan dictionaries
        """
        # Get items to produce based on recent sales
        items_to_produce = self.get_items_to_produce(agent, max_items)

        if not items_to_produce:
            print("No recent sales found. No production plans created.")
            return []

        print(f"Creating production plans for {len(items_to_produce)} items based on recent sales:")
        for item in items_to_produce:
            print(f"  - {item}")
        print()

        # Create plans for each item
        plans = []
        for item_name in items_to_produce:
            try:
                plan = self.create_production_plan_with_llm(agent, item_name, time_step)
                if plan:
                    plans.append(plan.package())
                    print(f"✓ Created plan for {item_name}: {plan.planned_quantity} units")
                else:
                    print(f"✗ Failed to create plan for {item_name}")
            except Exception as e:
                print(f"✗ Error creating plan for {item_name}: {e}")

        return plans

    def package(self) -> List[Dict[str, Any]]:
        """Package all plans for saving."""
        return [plan.package() for plan in self.production_plans]

    def execute_production_for_all_agents(self, agents, time_step: int = 0) -> Dict[str, Any]:
        """
        Execute production planning for all agents based on their recent sales.

        Parameters:
            agents: List of GenerativeAgent objects
            time_step: Current simulation time step

        Returns:
            Dict with production results for each agent
        """
        production_results = {}

        for agent in agents:
            agent_name = agent.scratch.get_fullname()

            try:
                # Get items to produce based on recent sales
                items_to_produce = agent.get_items_to_produce_from_sales(max_items=5)

                if items_to_produce:
                    # Create production plans for recent sales items
                    plans = agent.create_production_plans_for_recent_sales(time_step, max_items=5)

                    executed_plans = []
                    total_cost = 0.0

                    # Execute each production plan
                    for plan_data in plans:
                        # Convert dict to ProductionPlan object for execution
                        plan = ProductionPlan(plan_data)

                        success = agent.execute_production_plan(plan, time_step)
                        if success:
                            executed_plans.append(plan_data)
                            # Calculate cost
                            current_inventory = agent.inventory.get_all_items_with_values().get(plan.item_name, {})
                            production_cost = current_inventory.get("production_cost_per_unit", 0.0)
                            total_cost += plan.planned_quantity * production_cost

                    production_results[agent_name] = {
                        'items_considered': items_to_produce,
                        'plans_created': len(plans),
                        'plans_executed': len(executed_plans),
                        'total_cost': total_cost,
                        'executed_plans': executed_plans
                    }

                    if DEBUG:
                        print(f"  {agent_name}: {len(executed_plans)}/{len(plans)} plans executed, cost: ${total_cost:.2f}")

                else:
                    production_results[agent_name] = {
                        'items_considered': [],
                        'plans_created': 0,
                        'plans_executed': 0,
                        'total_cost': 0.0,
                        'executed_plans': []
                    }
                    if DEBUG:
                        print(f"  {agent_name}: No recent sales found for production planning")

            except Exception as e:
                print(f"Error in production planning for {agent_name}: {e}")
                production_results[agent_name] = {
                    'error': str(e),
                    'plans_executed': 0,
                    'total_cost': 0.0
                }

        return production_results