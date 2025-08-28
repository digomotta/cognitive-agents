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

        print(f"Analyzing trade at time step {time_step}")
        print(f"Conversation text: {conversation_text}")

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



    def execute_buyer_side(
        buyer_name: str,
        item_name: str,
        quantity: int,
        price: float,
        seller_name: str,
        time_step: int
    ):
        """
        Execute the buyer's side of a transaction by finding the buyer agent and updating their inventory.
        This should be called when a trade is detected from the seller's perspective.
        """
        return None

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

        model_to_use = model or self.model

        json_response = self.analyze_trade(
            agents=agents,
            conversation_text=normalized_text,
            time_step=time_step,
        )

        print(json_response)

        # Return True if at least one item was parsed
        try:
            return bool(json_response and isinstance(json_response, dict) and json_response.get("items"))
        except Exception:
            return False
