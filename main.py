from simulation_engine.settings import *
from simulation_engine.global_methods import *

from agent_bank.navigator import *
from generative_agent.generative_agent import *

from testing.memories.rowan_greenwood_memories import *
from testing.memories.jasmine_carter_memories import *
from generative_agent.modules.conversation_trade_analyzer import ConversationTradeAnalyzer
from generative_agent.modules.conversation_interaction import ConversationBasedInteraction

#from testing.questions.rowan_greenwood_questions import *


def chat_session(generative_agent, stateless=False): 
  conversation_id = "conversation_001"

  print (f"Start chatting with {generative_agent.scratch.get_fullname()}.")
  print ("Type 'bye' to exit.")
  print ("")

  context = input("First, describe the context of this conversation: ")
  user_name = input("And what is your name: ")
  print ("")

  # Start new interaction in working memory
  generative_agent.working_memory.start_new_interaction(context)
  
  curr_convo = []

  try:
    while True: 
      if stateless: 
        curr_convo = []
        # For stateless mode, clear working memory each turn
        generative_agent.working_memory.clear()

      user_input = input("You: ").strip()
      curr_convo += [[user_name, user_input]]

      if user_input.lower() == "bye":
        print(generative_agent.Act(conversation_id,curr_convo, context)) 
        break

      response = generative_agent.Act(conversation_id, curr_convo, context)  
      curr_convo += [[generative_agent.scratch.get_fullname(), response]]
      print(f"{generative_agent.scratch.get_fullname()}: {response}")
  
  finally:
    # Always clear working memory when conversation ends
    print("\n=== Conversation ended. Clearing working memory ===")
    generative_agent.working_memory.end_interaction()


def setup_agent_inventory(agent, agent_name):
  """Set up initial inventory for an agent and clear history."""
  # Clear existing inventory and records
  agent.inventory.items.clear()
  agent.inventory.records.clear()
  agent.save()  # Save the cleared inventory to JSON files
  
  if agent_name == "rowan_greenwood":
    # Rowan: Real estate agent with herbal products
    agent.add_to_inventory("herbal_tea", 5, 1, 15.00, "Calming herbal tea blend")
    agent.add_to_inventory("cannabis", 10, 1, 8.50, "Medicinal cannabis")
    agent.add_to_inventory("property_contracts", 3, 1, 200.00, "Real estate contracts ready to sign")
    agent.add_to_inventory("cash", 150, 1, 1.00, "Starting business cash")
    
  elif agent_name == "jasmine_carter":
    # Jasmine: Math student with academic supplies
    agent.add_to_inventory("textbooks", 4, 1, 85.00, "Advanced mathematics textbooks")
    agent.add_to_inventory("graphing_calculator", 1, 1, 120.00, "TI-84 Plus calculator")
    agent.add_to_inventory("notebooks", 8, 1, 3.50, "High-quality notebooks")
    agent.add_to_inventory("tutoring_sessions", 2, 1, 40.00, "One-hour math tutoring sessions")
    agent.add_to_inventory("cash", 75, 1, 1.00, "Student savings")

  agent.save()  # Save the cleared inventory to JSON files


def build_agent(): 
  # Build Rowan
  rowan = GenerativeAgent("Synthetic_Base", "rowan_greenwood")
  for m in rowan_memories: 
    rowan.remember(m)
  setup_agent_inventory(rowan, "rowan_greenwood")
  rowan.save("Synthetic", "rowan_greenwood")
  
  # Build Jasmine  
  jasmine = GenerativeAgent("Synthetic_Base", "jasmine_carter")
  for m in jasmine_memories:
    jasmine.remember(m)
  setup_agent_inventory(jasmine, "jasmine_carter")
  jasmine.save("Synthetic", "jasmine_carter")
  
  print("Both agents built with fresh inventories!")


def interview_agent(): 
  curr_agent = GenerativeAgent("Synthetic", "rowan_greenwood")
  chat_session(curr_agent, True)


def chat_with_agent(): 
  #curr_agent = GenerativeAgent("SyntheticCS222", "rowan_greenwood")
  curr_agent = GenerativeAgent("Synthetic", "jasmine_carter")
  chat_session(curr_agent, False)


def ask_agent_to_reflect(): 
  curr_agent = GenerativeAgent("Synthetic", "rowan_greenwood")
  #curr_agent.reflect("Reflect on your goal in life")
  curr_agent.reflect("How have your libertarian beliefs influenced your approach to managing your real estate business and navigating financial challenges?")


def test_inventory_in_conversation():
  """Test that agents can access their inventory during conversations."""
  print("=== Testing Inventory in Conversations ===")
  
  rowan = GenerativeAgent("Synthetic", "rowan_greenwood")
  print(f"Rowan's current inventory:\n{rowan.get_all_items_with_values()}")
  
  print("\nNow let's chat with Rowan and ask about his inventory...")
  print("Try asking: 'What do you have with you?' or 'What items do you have?'")
  print("The agent should be able to see his inventory in the conversation.")
  
  chat_session(rowan, False)



def test_conversation(testing_mode=True):
  """
  Demonstrate the new conversation-based trading system that analyzes 
  the complete conversation and executes trades at the end.
  
  Args:
    testing_mode: If True, don't save changes to agent files (default: True for safety)
  """
  print("=== Conversation-Based Trading Demo ===")
  print("This demo uses the new system that reads the entire conversation")
  if testing_mode:
    print("🧪 TESTING MODE: Changes will NOT be saved to agent files")
  else:
    print("💾 LIVE MODE: Changes WILL be saved to agent files")
  print()
  
  agents = ['rowan_greenwood', 'jasmine_carter']
  # Load existing agents
  agent1 = GenerativeAgent("Synthetic", agents[0])
  agent2 = GenerativeAgent("Synthetic", agents[1])
  
  print("Initial inventories:")
  print(f"Rowan ({agent1.scratch.get_fullname()}): {agent1.get_all_items_with_values()}")
  print(f"Jasmine ({agent2.scratch.get_fullname()}): {agent2.get_all_items_with_values()}")
  print()
  
  # Context for trading
  context = "You are at a local market."
  
  # Use a unique conversation ID
  conversation_id = "market_conversation_001"
  
  # Start conversation with conversation-based approach (no real-time trade detection)
  curr_dialogue = []
  
  print("=== Starting Conversation (No Real-Time Trade Detection) ===")
  
  # Let them have several exchanges
  for turn in range(12):
    # if turn == 0:
    #   curr_dialogue.append(["Rowan", "Hello! Welcome to my market stall. I have some excellent herbal teas and remedies for sale today."])
    # else:

    agent1_response, sales1, ended = agent1.Act(conversation_id, curr_dialogue, context, turn)
    curr_dialogue.append([f"{agent1.scratch.get_fullname()}", agent1_response])
    #print(f"{agent1.scratch.get_fullname()}: {agent1_response}")
    if ended == True:
      print(f"Conversation ended at time step {turn}")
      ConversationBasedInteraction().end_conversation(agents=[agent1, agent2], conversation_id=conversation_id, time_step=turn)
      break

    agent2_response, sales2, ended = agent2.Act(conversation_id, curr_dialogue, context, turn)
    curr_dialogue.append([f"{agent2.scratch.get_fullname()}", agent2_response])
    #print(f"{agent2.scratch.get_fullname()}: {agent2_response}")
    print()

    if ended == True:
      print(f"Conversation ended at time step {turn}")
      ConversationBasedInteraction().end_conversation(agents=[agent1, agent2], conversation_id=conversation_id, time_step=turn)
      break

    if sales1 == True or sales2 == True:
      print(f"Sales detected at time step {turn}")
      sales_manager = ConversationTradeAnalyzer()
      sales_manager.execute_trade(agents=[agent1, agent2],
      conversation_id=conversation_id,
      conversation_text=curr_dialogue,
      context=context,
      time_step=turn)

  print(f"Rowan's inventory: {agent1.get_all_items_with_values()}")
  print(f"Jasmine's inventory: {agent2.get_all_items_with_values()}")
  print()
  
  return agent1, agent2


def test_interaction_summary(testing_mode=True):
  """Test the interaction summarization feature with automatic end_conversation."""
  print("=== Testing Automatic Interaction Summary Feature ===")
  
  # Load existing agents
  rowan = GenerativeAgent("Synthetic", "rowan_greenwood")
  jasmine = GenerativeAgent("Synthetic", "jasmine_carter")
  
  print(f"Testing with {rowan.scratch.get_fullname()} and {jasmine.scratch.get_fullname()}")
  print()
  
  # Create a sample conversation for testing
  conversation_id = "test_summary_001"
  context = "Meeting at the local farmers market"
  
  # Start interaction in working memory
  rowan.working_memory.start_new_interaction(context, conversation_id)
  jasmine.working_memory.start_new_interaction(context, conversation_id)
  
  # Simulate a conversation with some trades
  sample_dialogue = [
    ["Rowan Greenwood", "Good morning! I've got some lovely herbal tea blends today. Fresh mint and chamomile, $15 each."],
    ["Jasmine Carter", "That sounds perfect for studying. I'll take one herbal tea please."],
    ["Rowan Greenwood", "Excellent choice! Just tap your digital cash on my machine."],
    ["Jasmine Carter", "Tapping my cash now. Thank you!"],
    ["Rowan Greenwood", "Transaction complete. That blend should help with focus and relaxation. Enjoy!"],
    ["Jasmine Carter", "Perfect timing before my calculus exam. Take care!"]
  ]
  
  # Add conversation turns to working memory
  for speaker, message in sample_dialogue:
    rowan.working_memory.add_conversation_turn(speaker, message)
    jasmine.working_memory.add_conversation_turn(speaker, message)
  
  # Simulate a trade record
  sample_trade = {
    "participants": {"seller": "Rowan Greenwood", "buyer": "Jasmine Carter"},
    "items": [{"name": "herbal_tea", "quantity": 1, "value": 15.0}],
    "time_step": 0
  }
  rowan.working_memory.record_trade(sample_trade)
  jasmine.working_memory.record_trade(sample_trade)
  
  print("Sample conversation:")
  print(rowan.working_memory.get_conversation_text())
  print()
  
  # Test the automatic summarization in end_conversation
  print("=== Testing Automatic Summarization ===")
  conversation_manager = ConversationBasedInteraction()
  
  # End conversation with testing mode (so agents aren't permanently saved)
  conversation_manager.end_conversation(
    agents=[rowan, jasmine], 
    conversation_id=conversation_id, 
    time_step=0, 
    testing_mode=testing_mode
  )
  
  print()
  print("✅ Test completed! The end_conversation method automatically:")
  print("   - Generated personalized summaries for each agent")
  print("   - Added summaries to their long-term memory") 
  print("   - Would save agents (skipped in testing mode)")
  print("   - Cleaned up working memory")


def main(): 
  # build_agent()
  # setup_agent_inventory(GenerativeAgent("Synthetic", "rowan_greenwood"), "rowan_greenwood")
  # setup_agent_inventory(GenerativeAgent("Synthetic", "jasmine_carter"), "jasmine_carter")
  # interview_agent()
  # chat_with_agent()
  # ask_agent_to_reflect()
  test_interaction_summary(testing_mode=False)



if __name__ == '__main__':
  main()
  