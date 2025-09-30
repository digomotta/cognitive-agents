from typing import Dict, List, Any, Tuple, Optional, TYPE_CHECKING
import json
from simulation_engine.gpt_structure import chat_safe_generate
from simulation_engine.llm_json_parser import extract_first_json_dict
from simulation_engine.settings import LLM_VERS, LLM_ANALYZE_VERS, LLM_PROMPT_DIR

if TYPE_CHECKING:
    from generative_agent.generative_agent import GenerativeAgent

class ConversationTradeAnalyzer:
    """
    Analyzes complete conversations to determine all trades that occurred
    and calculates the net result for each participant.
    """

    def __init__(self, model: str = LLM_ANALYZE_VERS):
        self.model = model

    def analyze_trade(
        self,
        agents: List['GenerativeAgent'],
        conversation_text: str,
        time_step: int,
    ) -> Dict[str, Any]:

        """
        Analyze conversation and return JSON with:
        {
          "participants": {"seller": str, "buyer": str},
          "items": [{"name": str, "quantity": int, "value": float}]
        }
        Also, here is the inventory for each participant, keyed by their name, with item names and quantities as close as possible to the inventory item names.
        """
        # Gather inventories for each agent, keyed by their full name
        inventories = {}
        for agent in agents:
            agent_name = agent.scratch.get_fullname() if hasattr(agent.scratch, "get_fullname") else getattr(agent, "name", agent.id)
            # get_all_items_with_values returns a dict: {name: {quantity, value_per_unit, total_value}}
            try:
                items_map = agent.get_all_items_with_values()
            except Exception:
                items_map = {}

            items_list = []
            if isinstance(items_map, dict):
                for item_name, meta in items_map.items():
                    try:
                        qty = int(meta.get("quantity", 0)) if isinstance(meta, dict) else 0
                    except Exception:
                        qty = 0
                    # Include unit price so the model can compute totals via prompt
                    try:
                        unit_price = float(
                            (meta.get("value_per_unit") if isinstance(meta, dict) else 0.0)
                            or (meta.get("value") if isinstance(meta, dict) else 0.0)
                            or 0.0
                        )
                    except Exception:
                        unit_price = 0.0
                    items_list.append({"name": str(item_name), "quantity": qty, "value": unit_price})
            elif isinstance(items_map, list):
                # Fallback if a list is ever returned
                for it in items_map:
                    if isinstance(it, dict):
                        try:
                            unit_price = float(it.get("value", 0.0) or 0.0)
                        except Exception:
                            unit_price = 0.0
                        items_list.append({
                            "name": str(it.get("name", "")),
                            "quantity": int(it.get("quantity", 0) or 0),
                            "value": unit_price
                        })
            inventories[agent_name] = items_list

        # Prepare inputs for the template
        inventories_json = json.dumps(inventories, indent=2)

        raw, _, _, _ = chat_safe_generate(
            prompt_input=[inventories_json, conversation_text],
            prompt_lib_file=f"{LLM_PROMPT_DIR}/generative_agent/interaction/trade_analysis_v1.txt",
            model=self.model,
            max_tokens=300
        )
        parsed = extract_first_json_dict(raw or "")

        if not isinstance(parsed, dict):
            return {"participants": {"seller": "", "buyer": ""}, "items": []}

        participants = parsed.get("participants") if isinstance(parsed.get("participants"), dict) else {}
        seller = str(participants.get("seller") or "")
        buyer = str(participants.get("buyer") or "")

        items = []
        raw_items = parsed.get("items")
        if isinstance(raw_items, list):
            for it in raw_items:
                if not isinstance(it, dict):
                    continue
                name = str(it.get("name") or "").strip()
                try:
                    quantity = int(it.get("quantity") or 0)
                except Exception:
                    quantity = 0
                try:
                    value = float(it.get("value") or 0)
                except Exception:
                    value = 0.0
                items.append({"name": name, "quantity": quantity, "value": value})

        return {"participants": {"seller": seller, "buyer": buyer}, "items": items, "time_step": time_step}

    def generate_failure_warning(self, agents: List['GenerativeAgent'], trade_data: Dict[str, Any]) -> str:
        """
        Generate a user-friendly warning message explaining why a trade failed.
        """
        participants = trade_data.get("participants", {})
        seller_name = participants.get("seller", "")
        buyer_name = participants.get("buyer", "")
        items = trade_data.get("items", [])
        
        if not seller_name or not buyer_name:
            return "⚠️ Trade failed: Could not identify buyer and seller"
        
        # Find agents and check for specific failure reasons
        seller_agent = None
        buyer_agent = None
        for agent in agents:
            agent_name = agent.scratch.get_fullname() if hasattr(agent.scratch, "get_fullname") else getattr(agent, "name", agent.id)
            if agent_name == seller_name:
                seller_agent = agent
            elif agent_name == buyer_name:
                buyer_agent = agent
        
        warnings = []
        
        # Check seller inventory issues
        if seller_agent:
            for item in items:
                item_name = item.get("name", "")
                quantity = item.get("quantity", 0)
                if item_name and quantity > 0:
                    available = seller_agent.inventory.get_item_quantity(item_name)
                    if available < quantity:
                        if available == 0:
                            warnings.append(f"{seller_name} is out of {item_name}")
                        else:
                            warnings.append(f"{seller_name} only has {available} {item_name} (needed {quantity})")
        
        # Check buyer cash issues
        if buyer_agent and items:
            total_cost = sum(item.get("value", 0.0) for item in items)
            if total_cost > 0:
                available_cash = buyer_agent.inventory.get_item_quantity("digital cash")
                if available_cash < int(total_cost):
                    warnings.append(f"{buyer_name} has insufficient funds (${available_cash} available, ${int(total_cost)} needed)")
        
        if warnings:
            return "⚠️ Trade failed: " + "; ".join(warnings)
        else:
            return "⚠️ Trade failed: Unknown reason"

    def get_trade_summary(
        self,
        conversation_text: str,
        participants: List[Dict[str, Any]]
    ) -> str:
        """
        Get a human-readable summary of trades that occurred in the conversation.
        """
        return None



    def execute_seller_trade(
        self,
        agents: List['GenerativeAgent'],
        trade_data: Dict[str, Any],
        testing_mode: bool = False
    ) -> bool:
        """
        Execute seller's side of trade using JSON data from analyze_trade.
        Removes sold items and adds cash to seller's inventory.
        
        Args:
            agents: List of agents involved in the conversation
            trade_data: JSON output from analyze_trade containing participants and items
            testing_mode: If True, don't save changes to JSON files
        
        Returns True if trade was successfully executed, False otherwise.
        """
        try:
            # Extract trade information
            participants = trade_data.get("participants", {})
            seller_name = participants.get("seller", "")
            buyer_name = participants.get("buyer", "")
            items = trade_data.get("items", [])
            time_step = trade_data.get("time_step", 0)
            
            if not seller_name or not buyer_name or not items:
                return False
            
            # Find the seller agent
            seller_agent = None
            for agent in agents:
                agent_name = agent.scratch.get_fullname() if hasattr(agent.scratch, "get_fullname") else getattr(agent, "name", agent.id)
                if agent_name == seller_name:
                    seller_agent = agent
                    break
            
            if not seller_agent:
                return False
            
            # Execute trade for each item
            total_success = True
            for item in items:
                item_name = item.get("name", "")
                quantity = item.get("quantity", 0)
                price = item.get("value", 0.0)
                
                if not item_name or quantity <= 0:
                    continue
                
                # Check if seller has the item in required quantity
                if not seller_agent.inventory.has_item(item_name, quantity):
                    # Record the failed trade attempt
                    reason = f"Insufficient inventory: needed {quantity}, have {seller_agent.inventory.get_item_quantity(item_name)}"
                    seller_agent.inventory.record_trade_failure(item_name, quantity, time_step, buyer_name, reason)
                    seller_agent.working_memory.record_sales_failure({
                        'item_attempted': item_name,
                        'quantity_attempted': quantity,
                        'reason': reason,
                        'trade_partner': buyer_name
                    })
                    seller_agent.scratch.total_sales_failures += 1
                    seller_agent.scratch.last_sales_failure_time = time_step
                    total_success = False
                    continue
                
                # Remove the sold item from seller's inventory
                success = seller_agent.inventory.sell_item(
                    item_name=item_name,
                    quantity=quantity,
                    time_step=time_step,
                    buyer=buyer_name,
                    price_per_unit=price / quantity if quantity > 0 else 0.0,
                    description=f"Sold {quantity} {item_name} to {buyer_name} for ${price}"
                )
                
                if not success:
                    # Record the failed trade attempt
                    reason = "Failed to remove item from inventory"
                    seller_agent.inventory.record_trade_failure(item_name, quantity, time_step, buyer_name, reason)
                    seller_agent.working_memory.record_sales_failure({
                        'item_attempted': item_name,
                        'quantity_attempted': quantity,
                        'reason': reason,
                        'trade_partner': buyer_name
                    })
                    seller_agent.scratch.total_sales_failures += 1
                    seller_agent.scratch.last_sales_failure_time = time_step
                    total_success = False
                    continue
                
                # Payment is automatically handled by sell_item() method
            
            # Save the updated inventory (unless in testing mode)
            if total_success and not testing_mode:
                seller_agent.save()
            
            return total_success
            
        except Exception as e:
            print(f"Error executing seller trade: {e}")
            return False

    def execute_buyer_trade(
        self,
        agents: List['GenerativeAgent'],
        trade_data: Dict[str, Any],
        testing_mode: bool = False
    ) -> bool:
        """
        Execute buyer's side of trade: remove cash and add purchased items to inventory.
        
        Args:
            agents: List of agents involved in the conversation
            trade_data: JSON output from analyze_trade containing participants and items
            testing_mode: If True, don't save changes to JSON files
        
        Returns True if trade was successfully executed, False otherwise.
        """
        try:
            # Extract trade information
            participants = trade_data.get("participants", {})
            seller_name = participants.get("seller", "")
            buyer_name = participants.get("buyer", "")
            items = trade_data.get("items", [])
            time_step = trade_data.get("time_step", 0)
            
            if not seller_name or not buyer_name or not items:
                return False
            
            # Find the buyer agent
            buyer_agent = None
            for agent in agents:
                agent_name = agent.scratch.get_fullname() if hasattr(agent.scratch, "get_fullname") else getattr(agent, "name", agent.id)
                if agent_name == buyer_name:
                    buyer_agent = agent
                    break
            
            if not buyer_agent:
                return False
            
            # Calculate total cost and check if buyer has enough cash
            total_cost = sum(item.get("value", 0.0) for item in items)
            if total_cost > 0 and not buyer_agent.inventory.has_item("digital cash", int(total_cost)):
                # Record the failed purchase attempt due to insufficient funds
                reason = f"Insufficient funds: needed ${total_cost}, have ${buyer_agent.inventory.get_item_quantity('digital cash')}"
                buyer_agent.working_memory.record_sales_failure({
                    'item_attempted': f"{len(items)} items",
                    'cost_attempted': total_cost,
                    'reason': reason,
                    'trade_partner': seller_name
                })
                buyer_agent.scratch.total_sales_failures += 1
                buyer_agent.scratch.last_sales_failure_time = time_step
                return False
            
            # Execute trade for each item
            total_success = True
            for item in items:
                item_name = item.get("name", "")
                quantity = item.get("quantity", 0)
                price = item.get("value", 0.0)
                
                if not item_name or quantity <= 0:
                    continue
                
                # Purchase the item (adds to inventory and handles payment automatically)
                success = buyer_agent.inventory.buy_item(
                    item_name=item_name,
                    quantity=quantity,
                    time_step=time_step,
                    seller=seller_name,
                    price_per_unit=price / quantity if quantity > 0 else 0.0,
                    description=f"Purchased {quantity} {item_name} from {seller_name} for ${price}"
                )
                
                if not success:
                    # Record the failed purchase
                    reason = "Failed to complete purchase transaction"
                    buyer_agent.working_memory.record_sales_failure({
                        'item_attempted': item_name,
                        'cost_attempted': price,
                        'reason': reason,
                        'trade_partner': seller_name
                    })
                    buyer_agent.scratch.total_sales_failures += 1
                    buyer_agent.scratch.last_sales_failure_time = time_step
                    total_success = False
            
            # Save the updated inventory (unless in testing mode)
            if total_success and not testing_mode:
                buyer_agent.save()
            
            return total_success
            
        except Exception as e:
            print(f"Error executing buyer trade: {e}")
            return False

    def execute_trade(
        self,
        agents: List['GenerativeAgent'],
        conversation_id: str,
        conversation_text: Any,
        context: str,
        time_step: int = 0,
        model: Optional[str] = None,
        testing_mode: bool = False
    ) -> bool:
        """
        If called, it means that the agent has detected a trade in the conversation.
        It will analyze the trade and execute it.
        It will return True if the trade was executed, False otherwise.
        
        Args:
            testing_mode: If True, don't save inventory changes to JSON files
        """
        # Normalize conversation text to string if a dialogue list is provided
        normalized_text: str
        if isinstance(conversation_text, list):
            try:
                normalized_text = "".join(
                    f"[{speaker}]: {message}\n" for speaker, message in conversation_text
                )
            except Exception:
                normalized_text = str(conversation_text)
        else:
            normalized_text = str(conversation_text)


        json_response = self.analyze_trade(
            agents=agents,
            conversation_text=normalized_text,
            time_step=time_step,
        )

        print(json_response)

        # Execute the trade if analysis was successful
        trade_executed = False
        if json_response and isinstance(json_response, dict) and json_response.get("items"):
            seller_success = self.execute_seller_trade(agents, json_response, testing_mode)
            buyer_success = self.execute_buyer_trade(agents, json_response, testing_mode)
            trade_executed = seller_success and buyer_success
            
            if trade_executed:
                print(f"Trade executed successfully: {json_response.get('participants', {}).get('seller', '')} sold items to {json_response.get('participants', {}).get('buyer', '')}")
                
                # Record trade in working memory for each agent
                for agent in agents:
                    agent.working_memory.record_trade(json_response)
                    
            else:
                print("Trade analysis detected but execution failed")
                if not seller_success:
                    print("- Seller side execution failed")
                if not buyer_success:
                    print("- Buyer side execution failed")

        # Return trade details if executed successfully, None otherwise
        try:
            if trade_executed and json_response:
                return {
                    'executed': True,
                    'trade_details': json_response,
                    'conversation_id': conversation_id,
                    'time_step': time_step,
                    'warning': None
                }
            else:
                # Generate warning message for failed trade
                warning = None
                if json_response and json_response.get("items"):
                    warning = self.generate_failure_warning(agents, json_response)
                
                return {
                    'executed': False,
                    'trade_details': json_response,
                    'conversation_id': conversation_id,
                    'time_step': time_step,
                    'warning': warning
                }
        except Exception:
            return {
                'executed': False, 
                'trade_details': None,
                'conversation_id': conversation_id,
                'time_step': time_step,
                'warning': "⚠️ Trade failed: System error during execution"
            }
