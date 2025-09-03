from simulation_engine.settings import *
from simulation_engine.global_methods import *

from agent_bank.navigator import *
from generative_agent.generative_agent import *

from testing.memories.rowan_greenwood_memories import *
from testing.memories.jasmine_carter_memories import *
from testing.memories.mina_kim_memories import *
from testing.memories.kemi_adebayo_memories import *
from generative_agent.modules.conversation_trade_analyzer import ConversationTradeAnalyzer
from generative_agent.modules.conversation_interaction import ConversationBasedInteraction
from markov_agent_chain import MarkovAgentChain, load_agents_for_chain

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
    agent.add_to_inventory("digital cash", 150, 1, 1.00, "Starting business cash")
    
  elif agent_name == "jasmine_carter":
    # Jasmine: Math student with academic supplies
    agent.add_to_inventory("textbooks", 4, 1, 85.00, "Advanced mathematics textbooks")
    agent.add_to_inventory("graphing_calculator", 1, 1, 120.00, "TI-84 Plus calculator")
    agent.add_to_inventory("notebooks", 8, 1, 3.50, "High-quality notebooks")
    agent.add_to_inventory("tutoring_sessions", 2, 1, 40.00, "One-hour math tutoring sessions")
    agent.add_to_inventory("digital cash", 75, 1, 1.00, "Student savings")
    
  elif agent_name == "mina_kim":
    # Mina: Korean beauty cosmetics expert
    agent.add_to_inventory("sheet_masks", 20, 1, 3.50, "Korean sheet masks - various types")
    agent.add_to_inventory("essence", 5, 1, 28.00, "Korean essence serums")
    agent.add_to_inventory("cushion_foundation", 3, 1, 35.00, "BB cushion foundations")
    agent.add_to_inventory("lip_tints", 8, 1, 12.00, "Korean gradient lip tints")
    agent.add_to_inventory("sunscreen", 4, 1, 22.00, "Korean SPF50+ sunscreens")
    agent.add_to_inventory("sleeping_masks", 6, 1, 18.00, "Overnight sleeping masks")
    agent.add_to_inventory("cleansing_oil", 3, 1, 25.00, "Double cleansing oils")
    agent.add_to_inventory("digital cash", 100, 1, 1.00, "K-beauty business earnings")
    
  elif agent_name == "kemi_adebayo":
    # Kemi: Nigerian tech entrepreneur with African superfood products
    agent.add_to_inventory("moringa_powder", 15, 1, 45.00, "High-protein moringa superfood powder")
    agent.add_to_inventory("baobab_fruit_powder", 10, 1, 55.00, "Vitamin C rich baobab powder")
    agent.add_to_inventory("hibiscus_extract", 8, 1, 35.00, "Antioxidant hibiscus extract capsules")
    agent.add_to_inventory("tiger_nut_flour", 12, 1, 25.00, "Gluten-free tiger nut flour")
    agent.add_to_inventory("african_yam_chips", 20, 1, 18.00, "Dehydrated nutrient-dense yam chips")
    agent.add_to_inventory("palm_fruit_oil", 6, 1, 40.00, "Unprocessed red palm oil")
    agent.add_to_inventory("research_reports", 3, 1, 200.00, "Proprietary food tech research and patents")
    agent.add_to_inventory("mobile_app_licenses", 2, 1, 500.00, "Nutrition education app licenses")
    agent.add_to_inventory("digital cash", 300, 1, 1.00, "Startup revenue and investment funds")

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
  
  # Build Mina
  mina = GenerativeAgent("Synthetic_Base", "mina_kim")
  for m in mina_memories:
    mina.remember(m)
  setup_agent_inventory(mina, "mina_kim")
  mina.save("Synthetic", "mina_kim")
  
  # Build Kemi
  kemi = GenerativeAgent("Synthetic_Base", "kemi_adebayo")
  for m in kemi_memories:
    kemi.remember(m)
  setup_agent_inventory(kemi, "kemi_adebayo")
  kemi.save("Synthetic", "kemi_adebayo")
  
  print("All agents built with fresh inventories!")


def interview_agent(): 
  curr_agent = GenerativeAgent("Synthetic", "rowan_greenwood")
  chat_session(curr_agent, True)


def chat_with_agent(): 
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


def test_markov_chain_simulation(testing_mode=True):
  """
  Run Markov chain simulation where each agent is a state.
  State transitions i→i trigger reflections, i→j trigger conversations.
  """
  print("=== Markov Agent Chain Simulation ===")
  
  # Load agents for the chain
  agent_names = ["rowan_greenwood", "jasmine_carter", "mina_kim", "kemi_adebayo"]
  agents = load_agents_for_chain("Synthetic", agent_names)
  
  if len(agents) < 2:
    print("Error: Could not load required agents")
    return None
  
  # Create Markov chain and run simulation
  chain = MarkovAgentChain()
  
  results = chain.run_markov_chain(
    agents=agents,
    context="Local community market and social interactions",
    num_steps=10,
    self_reflection_prob=0.3,  # 30% chance to stay in same state (reflect)
    interaction_prob=0.7,      # 70% chance to transition to other agent (converse)
    conversation_max_turns=8,
    testing_mode=testing_mode
  )
  
  print("=== Simulation Results ===")
  print(f"Total conversations: {results['conversation_count']}")
  print(f"Total reflections: {results['reflection_count']}")
  print(f"Final agent state: {results['final_agent']}")
  
  return results


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
  # Simplified main for multi-agent Markov chain interactions
  # build_agent()
  # interview_agent()
  # chat_with_agent()
  # ask_agent_to_reflect()
  
  # Use the new Markov agent chain system
  test_markov_chain_simulation(testing_mode=True)



if __name__ == '__main__':
  main()
  