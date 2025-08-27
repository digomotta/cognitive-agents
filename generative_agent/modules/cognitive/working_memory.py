from typing import Dict, List, Any, Set
import json
from datetime import datetime

class WorkingMemory:
    """
    Working memory for agents to track current conversation context,
    recent memories, inventory state, and processed trades.
    """
    
    def __init__(self):
        # Current conversation context
        self.current_conversation: List[List[str]] = []
        self.conversation_context: str = ""
        
        # Recalled memories for current interaction
        self.recalled_memories: List[str] = []
        
        # Current inventory snapshot
        self.inventory_snapshot: Dict[str, Any] = {}
        
        # Trade processing tracking
        self.processed_trades: Set[int] = set()  # Hashes of processed conversation segments
        self.recent_trades: List[Dict[str, Any]] = []
        
        # Interaction state
        self.interaction_id: str = ""
        self.last_update_time: float = 0
        self.turn_count: int = 0
        
        # Cross-agent transaction tracking
        self.pending_purchase: Dict[str, Any] = {}  # For handling buyer side of transactions
    
    def start_new_interaction(self, context: str = "", interaction_id: str = ""):
        """Start a new interaction, clearing conversation-specific state."""
        self.current_conversation.clear()
        self.conversation_context = context
        self.recalled_memories.clear()
        self.processed_trades.clear()
        self.recent_trades.clear()
        self.interaction_id = interaction_id or str(datetime.now().timestamp())
        self.turn_count = 0
        self.last_update_time = datetime.now().timestamp()
    
    def add_conversation_turn(self, speaker: str, message: str):
        """Add a new turn to the current conversation."""
        self.current_conversation.append([speaker, message])
        self.turn_count += 1
        self.last_update_time = datetime.now().timestamp()
    
    def update_inventory_snapshot(self, inventory_data: Dict[str, Any]):
        """Update the current inventory snapshot."""
        self.inventory_snapshot = inventory_data.copy()
        self.last_update_time = datetime.now().timestamp()
    
    def add_recalled_memory(self, memory_content: str):
        """Add a recalled memory to working memory."""
        if memory_content not in self.recalled_memories:
            self.recalled_memories.append(memory_content)
    
    def recall_memories_from_stream(self, agent: 'GenerativeAgent', anchor: str, n_count: int = 10):
        """
        Recall relevant memories from long-term memory stream and add to working memory.
        This bridges working memory with the agent's long-term memory_stream.
        """
        # Clear previous recalled memories for this interaction
        self.recalled_memories.clear()
        
        try:
            # Use the agent's memory_stream to retrieve relevant memories
            from simulation_engine.settings import DEBUG
            memories = agent.memory_stream.retrieve([anchor], time_step=0, n_count=n_count, verbose=DEBUG)
            
            # Add retrieved memories to working memory
            for node_list in memories.values():
                for memory_node in node_list:
                    self.add_recalled_memory(memory_node.content)
                    
        except Exception as e:
            print(f"Error recalling memories: {e}")
    
    def generate_agent_description(self, agent: 'GenerativeAgent', anchor: str) -> str:
        """
        Generate agent description using working memory context.
        This replaces _utterance_agent_desc and centralizes it in working memory.
        """
        # Start with agent's basic information
        agent_desc = ""
        agent_desc += f"Self-description: {agent.scratch.self_description}\n"
        agent_desc += f"Speech pattern: {agent.scratch.speech_pattern}\n"
        
        # Recall relevant memories if not already done for this interaction
        if not self.recalled_memories or anchor not in str(self.recalled_memories):
            self.recall_memories_from_stream(agent, anchor)
        
        # Add recalled memories to description
        for memory in self.recalled_memories:
            agent_desc += f"Memory: {memory}\n"
        
        # Add current inventory information
        agent_desc += f"\nCurrent Inventory:\n{agent.get_total_inventory_value()}\n"
        
        # Add current conversation context if available
        if self.conversation_context:
            agent_desc += f"\nConversation Context: {self.conversation_context}\n"
        
        return agent_desc
    
    def mark_conversation_processed(self, conversation_segment: str) -> bool:
        """
        Mark a conversation segment as processed for trades.
        Returns False if already processed, True if newly marked.
        """
        conversation_hash = hash(conversation_segment.strip())
        if conversation_hash in self.processed_trades:
            return False
        self.processed_trades.add(conversation_hash)
        return True
    
    def record_trade(self, trade_data: Dict[str, Any]):
        """Record a trade that occurred."""
        trade_record = {
            **trade_data,
            "timestamp": datetime.now().timestamp(),
            "interaction_id": self.interaction_id,
            "turn_count": self.turn_count
        }
        self.recent_trades.append(trade_record)
    
    def get_conversation_text(self) -> str:
        """Get the current conversation as formatted text."""
        return "\n".join([f"[{row[0]}]: {row[1]}" for row in self.current_conversation])
    
    def get_state_summary(self) -> str:
        """Get a summary of current working memory state."""
        return f"""Working Memory State:
- Conversation turns: {self.turn_count}
- Recalled memories: {len(self.recalled_memories)}
- Inventory items: {len(self.inventory_snapshot)}
- Processed trade segments: {len(self.processed_trades)}
- Recent trades: {len(self.recent_trades)}
- Last update: {datetime.fromtimestamp(self.last_update_time).strftime('%H:%M:%S')}"""
    
    def end_interaction(self):
        """End the current interaction and clear working memory."""
        print(f"Ending interaction {self.interaction_id} with {self.turn_count} turns")
        self.clear()
    
    def clear(self):
        """Clear all working memory."""
        self.current_conversation.clear()
        self.conversation_context = ""
        self.recalled_memories.clear()
        self.inventory_snapshot.clear()
        self.processed_trades.clear()
        self.recent_trades.clear()
        self.interaction_id = ""
        self.turn_count = 0
        self.last_update_time = 0
    
    def package(self) -> Dict[str, Any]:
        """Package working memory for serialization."""
        return {
            "current_conversation": self.current_conversation,
            "conversation_context": self.conversation_context,
            "recalled_memories": self.recalled_memories,
            "inventory_snapshot": self.inventory_snapshot,
            "processed_trades": list(self.processed_trades),
            "recent_trades": self.recent_trades,
            "interaction_id": self.interaction_id,
            "last_update_time": self.last_update_time,
            "turn_count": self.turn_count
        }
    
    def load_from_package(self, data: Dict[str, Any]):
        """Load working memory from serialized data."""
        self.current_conversation = data.get("current_conversation", [])
        self.conversation_context = data.get("conversation_context", "")
        self.recalled_memories = data.get("recalled_memories", [])
        self.inventory_snapshot = data.get("inventory_snapshot", {})
        self.processed_trades = set(data.get("processed_trades", []))
        self.recent_trades = data.get("recent_trades", [])
        self.interaction_id = data.get("interaction_id", "")
        self.last_update_time = data.get("last_update_time", 0)
        self.turn_count = data.get("turn_count", 0)