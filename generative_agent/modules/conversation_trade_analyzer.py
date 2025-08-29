from typing import Dict, List, Any, Tuple, Optional, TYPE_CHECKING
import json
from simulation_engine.gpt_structure import gpt_request
from simulation_engine.llm_json_parser import extract_first_json_dict
from simulation_engine.settings import LLM_VERS, LLM_ANALYZE_VERS

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
                    items_list.append({"name": str(item_name), "quantity": qty})
            elif isinstance(items_map, list):
                # Fallback if a list is ever returned
                for it in items_map:
                    if isinstance(it, dict):
                        items_list.append({
                            "name": str(it.get("name", "")),
                            "quantity": int(it.get("quantity", 0) or 0)
                        })
            inventories[agent_name] = items_list

        instruction = (
            "You extract a single commerce transaction from a conversation. "
            "Reply with JSON only. Schema: {\"participants\":{\"seller\":str,\"buyer\":str},\"items\":[{\"name\":str,\"quantity\":int,\"value\":float}]} . "
            "If a numeric field is missing/ambiguous use 0. Do not add any extra keys or text. "
            "You are also provided with the inventory of each participant, keyed by their name, as follows:\n"
            f"{json.dumps(inventories, indent=2)}\n"
            "Match or rename item names in your output as close as possible to the inventory item names."
            "If the values was not provided, use the value from the inventory."
        )

        prompt = (
            f"{instruction}\n\nConversation:\n{conversation_text}\n\nJSON only:"
        )

        raw = gpt_request(prompt, model=self.model, max_tokens=300)
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
        trade_data: Dict[str, Any]
    ) -> bool:
        """
        Execute seller's side of trade using JSON data from analyze_trade.
        Removes sold items and adds cash to seller's inventory.
        
        Args:
            agents: List of agents involved in the conversation
            trade_data: JSON output from analyze_trade containing participants and items
        
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
                    total_success = False
                    continue
                
                # Remove the sold item from seller's inventory
                success = seller_agent.inventory.trade_item(
                    item_name=item_name,
                    quantity=quantity,
                    is_giving=True,
                    time_step=time_step,
                    trade_partner=buyer_name,
                    description=f"Sold {quantity} {item_name} to {buyer_name} for ${price}"
                )
                
                if not success:
                    total_success = False
                    continue
                
                # Add cash to seller's inventory if price > 0
                if price > 0:
                    seller_agent.inventory.trade_item(
                        item_name="cash",
                        quantity=int(price),
                        is_giving=False,
                        time_step=time_step,
                        trade_partner=buyer_name,
                        value=1.0,
                        description=f"Received ${price} from selling {quantity} {item_name} to {buyer_name}"
                    )
            
            # Save the updated inventory
            if total_success:
                seller_agent.save()
            
            return total_success
            
        except Exception as e:
            print(f"Error executing seller trade: {e}")
            return False

    def execute_buyer_trade(
        self,
        agents: List['GenerativeAgent'],
        trade_data: Dict[str, Any]
    ) -> bool:
        """
        Execute buyer's side of trade: remove cash and add purchased items to inventory.
        
        Args:
            agents: List of agents involved in the conversation
            trade_data: JSON output from analyze_trade containing participants and items
        
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
            if total_cost > 0 and not buyer_agent.inventory.has_item("cash", int(total_cost)):
                return False
            
            # Execute trade for each item
            total_success = True
            for item in items:
                item_name = item.get("name", "")
                quantity = item.get("quantity", 0)
                price = item.get("value", 0.0)
                
                if not item_name or quantity <= 0:
                    continue
                
                # Add the purchased item to buyer's inventory
                buyer_agent.inventory.trade_item(
                    item_name=item_name,
                    quantity=quantity,
                    is_giving=False,
                    time_step=time_step,
                    trade_partner=seller_name,
                    value=price / quantity if quantity > 0 else 0.0,
                    description=f"Purchased {quantity} {item_name} from {seller_name} for ${price}"
                )
                
                # Remove cash from buyer's inventory if price > 0
                if price > 0:
                    success = buyer_agent.inventory.trade_item(
                        item_name="cash",
                        quantity=int(price),
                        is_giving=True,
                        time_step=time_step,
                        trade_partner=seller_name,
                        description=f"Paid ${price} for {quantity} {item_name} from {seller_name}"
                    )
                    
                    if not success:
                        total_success = False
            
            # Save the updated inventory
            if total_success:
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
        model: Optional[str] = None
    ) -> bool:
        """
        If called, it means that the agent has detected a trade in the conversation.
        It will analyze the trade and execute it.
        It will return True if the trade was executed, False otherwise.
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
            seller_success = self.execute_seller_trade(agents, json_response)
            buyer_success = self.execute_buyer_trade(agents, json_response)
            trade_executed = seller_success and buyer_success
            
            if trade_executed:
                print(f"Trade executed successfully: {json_response.get('participants', {}).get('seller', '')} sold items to {json_response.get('participants', {}).get('buyer', '')}")
            else:
                print("Trade analysis detected but execution failed")
                if not seller_success:
                    print("- Seller side execution failed")
                if not buyer_success:
                    print("- Buyer side execution failed")

        # Return True if trade was analyzed and executed successfully
        try:
            return trade_executed
        except Exception:
            return False
