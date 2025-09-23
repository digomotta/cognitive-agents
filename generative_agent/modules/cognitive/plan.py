from typing import Dict, List, Any, Optional
import json
import os
from simulation_engine.gpt_structure import gpt_request, generate_prompt
from simulation_engine.settings import LLM_VERS

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
        print('Prompt: ', prompt)

        # Get LLM response
        response = gpt_request(prompt, model=LLM_VERS)
        print('LLM response: ', response)

        # Check if response contains an error
        if response.startswith("GENERATION ERROR"):
            print(f"LLM generation failed: {response}")
            plan_data = {"planned_quantity": 0, "reasoning": f"LLM generation failed: {response}"}
        else:
            # Parse the JSON response
            try:
                plan_data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                plan_data = {"planned_quantity": 0, "reasoning": f"Failed to parse LLM response: {str(e)}"}
                print(f"Raw response: {response}")

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
            print(f"No valid production plan provided")
            return False

        # Get current inventory data for production cost
        current_inventory = agent.inventory.get_all_items_with_values().get(plan.item_name, {})
        production_cost_per_unit = current_inventory.get('production_cost_per_unit', 0.0)

        if production_cost_per_unit <= 0:
            print(f"No production cost defined for {plan.item_name}")
            return False

        # Calculate total production cost
        total_cost = plan.planned_quantity * production_cost_per_unit

        # Check if agent has enough cash
        available_cash = agent.get_inventory_quantity("digital cash")
        if available_cash < total_cost:
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

    def package(self) -> List[Dict[str, Any]]:
        """Package all plans for saving."""
        return [plan.package() for plan in self.production_plans]