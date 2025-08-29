from typing import List, Tuple, Dict, Any
import json
from simulation_engine.settings import * 
from simulation_engine.global_methods import *
from simulation_engine.gpt_structure import *
from simulation_engine.llm_json_parser import *
from .conversation_trade_analyzer import ConversationTradeAnalyzer
import re
import json

# Import at module level to avoid circular imports in function
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from generative_agent.generative_agent import GenerativeAgent


def run_LLM_generate_utterance(
    agent_desc: str, 
    str_dialogue: str,
    context: str,
    prompt_version: str = "1",
    model: str = "gpt-5",  
    verbose: bool = DEBUG) -> Tuple[Dict[str, Any], List[Any]]:
  """
  Generate an utterance using GPT based on the agent description, dialogue, and context.
  (Copied from original interaction.py to maintain compatibility)
  """
  def create_prompt_input(
    agent_desc: str, 
    str_dialogue: str, 
    context: str) -> List[str]:
    return [agent_desc, context, str_dialogue]        

  def _func_clean_up(gpt_response: str, prompt: str = "") -> Dict[str, Any]:
    """
    Extract response data as a dictionary from a JSON-like response.
    Returns dict with "utterance", "sales", and "ended" keys.
    """
    s = (gpt_response or "").strip()
    result = {"utterance": "", "sales": False, "ended": False}

    # Try full JSON parse first
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict) and "utterance" in parsed:
            result["utterance"] = parsed["utterance"]
            result["sales"] = bool(parsed.get("Sales Done") or parsed.get("sales_done") or parsed.get("sales"))
            # Support multiple possible keys for conversation end flag
            keys = [
                "ended",
                "end",
                "conversation_ended",
                "conversationEnded",
            ]
            found_any = any(k in parsed for k in keys)
            if found_any:
                result["ended"] = bool(
                    parsed.get("ended")
                    or parsed.get("end")
                    or parsed.get("conversation_ended")
                    or parsed.get("conversationEnded")
                )
            return result
    except Exception:
        pass  # fallback to regex

    # Regex fallback for utterance
    m = re.search(r'"utterance"\s*:\s*"(?P<val>.*?)"', s, re.DOTALL)
    if not m:
        print(f"ERROR: Failed to parse JSON from response: {gpt_response}...")
        result["utterance"] = s
        return result

    val = m.group("val")
    try:
        safe = (
            val.replace("\\", "\\\\")
               .replace('"', '\\"')
               .replace("\r", "\\r")
               .replace("\n", "\\n")
        )
        result["utterance"] = json.loads(f'"{safe}"')
    except Exception:
        result["utterance"] = val

    # Regex fallback for Sales Done
    m2 = re.search(r'"Sales Done"\s*:\s*(true|false)', s, re.IGNORECASE)
    result["sales"] = bool(m2 and m2.group(1).lower() == "true")

    # Regex fallback for ended
    m3 = re.search(r'"ended"\s*:\s*(true|false)', s, re.IGNORECASE)
    if m3:
        result["ended"] = m3.group(1).lower() == "true"

    return result


  def _get_fail_safe() -> None:
    return None

  # Set up the prompt file path
  prompt_lib_file = f"{LLM_PROMPT_DIR}/generative_agent/interaction/utternace/utterance_v2.txt" 

  # Create the prompt input
  prompt_input = create_prompt_input(agent_desc, str_dialogue, context) 

  # Get the fail-safe response
  fail_safe = _get_fail_safe() 

  # Generate the utterance using the chat_safe_generate function
  output, prompt, prompt_input, fail_safe = chat_safe_generate(
    prompt_input, prompt_lib_file, model, 1, fail_safe, 
    _func_clean_up, verbose)

  return output, [output, prompt, prompt_input, fail_safe]


class ConversationBasedInteraction:
    """
    Manages conversations with trade analysis done at the end of complete conversations
    instead of real-time during each turn.
    """
    
    def __init__(self):
        self.trade_analyzer = ConversationTradeAnalyzer()
        self.active_conversations = {}  # Track ongoing conversations
    
    def start_conversation(
        self, 
        conversation_id: str, 
        participants: List['GenerativeAgent'],
        context: str = ""
    ):
        """Start a new conversation session."""
        self.active_conversations[conversation_id] = {
            "participants": participants,
            "dialogue": [],
            "context": context,
            "trades_executed": False
        }
        
        # Initialize working memory for each participant
        for agent in participants:
            agent.working_memory.start_new_interaction(context, conversation_id)
    
    def generate_utterance(
        self, 
        agent: 'GenerativeAgent', 
        conversation_id: str,
        curr_dialogue: [List[str]], 
        context: str
    ) -> str:
        """
        Generate utterance without real-time trade detection.
        Trade detection happens only at conversation end.
        """
        
        if conversation_id not in self.active_conversations:
            # Start conversation if not already started
            self.start_conversation(conversation_id, [agent], context)
        
        # Update working memory with current dialogue
        conversation_data = self.active_conversations[conversation_id]
        
        for speaker, message in curr_dialogue:
            if [speaker, message] not in agent.working_memory.current_conversation:
                agent.working_memory.add_conversation_turn(speaker, message)
        
        # Create dialogue string and anchor for memory retrieval
        str_dialogue = "".join(f"[{row[0]}]: {row[1]}\n" for row in curr_dialogue)
        str_dialogue += f"[{agent.scratch.get_fullname()}]: "
        anchor = str_dialogue
        
        # Use working memory to generate agent description
        agent_desc = agent.working_memory.generate_agent_description(agent, anchor)
        
        # Generate response using LLM (Trade detection)
        result_dict, _ = run_LLM_generate_utterance(
                 agent_desc, str_dialogue, context, "1", LLM_ANALYZE_VERS)

        print(f"result_dict: {result_dict}")

        # Add agent's response to working memory and conversation
        agent.working_memory.add_conversation_turn(agent.scratch.get_fullname(), result_dict["utterance"])
        conversation_data["dialogue"].append([agent.scratch.get_fullname(), result_dict["utterance"]])
        
        return result_dict["utterance"], result_dict["sales"], result_dict["ended"]
    
    def end_conversation(self, agents: List['GenerativeAgent'], conversation_id: str, time_step: int = 0, testing_mode: bool = False) -> bool:
        """ End Conversation and save to the memory file of each agent + the trade summary. """

        print("=== Ending Conversation ===")
        
        for agent in agents:
            # Generate personalized summary from agent's perspective
            interaction_summary = agent.working_memory.summarize_interaction(agent)
            print(f"{agent.scratch.get_fullname()}'s summary: '{interaction_summary}'")
            
            # Add summary to long-term memory
            agent.remember(interaction_summary, time_step)
            
            # Save agent with new memory (unless in testing mode)
            if not testing_mode:
                ########
                # Is it saving into long-term memory??
                ########
                agent.save()
                print(f"✅ {agent.scratch.get_fullname()} saved with interaction summary")
            else:
                print(f"🧪 {agent.scratch.get_fullname()} summary generated (not saved - testing mode)")
            
            # Clear working memory
            agent.working_memory.clear()

        print("=== Conversation Ended ===")
        return True
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """Get a summary of trades in the conversation."""
        return


# Global instance for conversation management
conversation_manager = ConversationBasedInteraction()


def utterance_conversation_based(
    agent: 'GenerativeAgent', 
    conversation_id: str,
    curr_dialogue: List[List[str]], 
    context: str,
    time_step: int
) -> str:
    """
    Generate utterance using conversation-based approach.
    """
    print("time_step: ", time_step)
    response, sales, ended = conversation_manager.generate_utterance(agent=agent,
    conversation_id=conversation_id,
    curr_dialogue=curr_dialogue,
    context=context)

    # if sales == True:

    #     sales_manager = ConversationTradeAnalyzer()
    #     sales_manager.execute_trade(agent=agent,
    #      conversation_id=conversation_id,
    #      conversation_text=curr_dialogue,
    #      context=context,
    #      time_step=time_step)

    return response, sales, ended


