from simulation_engine.settings import *
from simulation_engine.global_methods import *

from agent_bank.navigator import *
from generative_agent.generative_agent import *

from testing.memories.rowan_greenwood_memories import *
from testing.memories.jasmine_carter_memories import *

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
  print(f"Rowan's current inventory:\n{rowan.get_total_inventory_value()}")
  
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
  
  # Load existing agents
  rowan = GenerativeAgent("Synthetic", "rowan_greenwood")
  jasmine = GenerativeAgent("Synthetic", "jasmine_carter")
  
  print("Initial inventories:")
  print(f"Rowan ({rowan.scratch.get_fullname()}): {rowan.get_total_inventory_value()}")
  print(f"Jasmine ({jasmine.scratch.get_fullname()}): {jasmine.get_total_inventory_value()}")
  print()
  
  # Context for trading
  context = "You are at a local market."
  
  # Use a unique conversation ID
  conversation_id = "market_conversation_001"
  
  # Start conversation with conversation-based approach (no real-time trade detection)
  curr_dialogue = []
  
  print("=== Starting Conversation (No Real-Time Trade Detection) ===")
  
  # Let them have several exchanges
  for turn in range(6):
    # Rowan's turn
    if turn == 0:
      curr_dialogue.append(["Rowan", "Hello! Welcome to my market stall. I have some excellent herbal teas and remedies for sale today."])
    else:
      rowan_response = rowan.Act(conversation_id, curr_dialogue, context)
      curr_dialogue.append(["Rowan", rowan_response])
      print(f"Rowan: {rowan_response}")
    
    # Jasmine's turn
    jasmine_response = jasmine.Act(conversation_id, curr_dialogue, context)
    curr_dialogue.append(["Jasmine", jasmine_response])
    print(f"Jasmine: {jasmine_response}")
    print()
  
  return rowan, jasmine


def main(): 
  # build_agent()
  # interview_agent()
  chat_with_agent()
  # ask_agent_to_reflect()
  #test_conversation()



if __name__ == '__main__':
  main()
  

































