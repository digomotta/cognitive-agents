from simulation_engine.settings import *
from simulation_engine.global_methods import *

from agent_bank.navigator import *
from generative_agent.generative_agent import *

from testing.memories.rowan_greenwood_memories import *
from testing.memories.jasmine_carter_memories import *
from testing.memories.mina_kim_memories import *
from testing.memories.kemi_adebayo_memories import *
from testing.memories.pema_sherpa_memories import *
from testing.memories.carlos_mendez_memories import *
from testing.memories.bianca_silva_memories import *
from testing.memories.mei_chen_memories import *
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
    agent.add_to_inventory("black_tea", 5, 1, 15.00, "Energetic black tea")
    agent.add_to_inventory("medicinal_cannabis", 10, 1, 8.50, "Medicinal cannabis")
    agent.add_to_inventory("property_contracts", 3, 1, 200.00, "Real estate contracts ready to sign")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Starting business cash")
    
  elif agent_name == "jasmine_carter":
    # Jasmine: Math student with academic supplies
    agent.add_to_inventory("textbooks", 4, 1, 85.00, "Advanced mathematics textbooks")
    agent.add_to_inventory("graphing_calculator", 1, 1, 120.00, "TI-84 Plus calculator")
    agent.add_to_inventory("notebooks", 8, 1, 3.50, "High-quality notebooks")
    agent.add_to_inventory("tutoring_sessions", 2, 1, 40.00, "One-hour math tutoring sessions")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Student savings")
    
  elif agent_name == "mina_kim":
    # Mina: Korean beauty cosmetics expert
    agent.add_to_inventory("sheet_masks", 20, 1, 3.50, "Korean sheet masks - various types")
    agent.add_to_inventory("essence", 5, 1, 28.00, "Korean essence serums")
    agent.add_to_inventory("cushion_foundation", 3, 1, 35.00, "BB cushion foundations")
    agent.add_to_inventory("lip_tints", 8, 1, 12.00, "Korean gradient lip tints")
    agent.add_to_inventory("sunscreen", 4, 1, 22.00, "Korean SPF50+ sunscreens")
    agent.add_to_inventory("sleeping_masks", 6, 1, 18.00, "Overnight sleeping masks")
    agent.add_to_inventory("cleansing_oil", 3, 1, 25.00, "Double cleansing oils")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "K-beauty business earnings")
    
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
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Startup revenue and investment funds")
    
  elif agent_name == "pema_sherpa":
    # Pema: Nepalese honey hunter with wild and mad honey
    agent.add_to_inventory("mad_honey", 3, 1, 150.00, "Sacred psychoactive honey from high-altitude rhododendron nectar")
    agent.add_to_inventory("wild_cliff_honey", 8, 1, 80.00, "Raw honey harvested from giant bee colonies on cliff faces")
    agent.add_to_inventory("mountain_flower_honey", 12, 1, 45.00, "Wildflower honey from high Himalayan meadows")
    agent.add_to_inventory("pine_honey", 6, 1, 55.00, "Dark honey with medicinal properties from pine tree secretions")
    agent.add_to_inventory("prayer_blessed_honey", 4, 1, 120.00, "Ceremonially blessed honey for spiritual and healing purposes")
    agent.add_to_inventory("traditional_climbing_gear", 2, 1, 300.00, "Handmade rope ladders and collection tools")
    agent.add_to_inventory("honey_medicinal_guide", 1, 1, 200.00, "Ancient family knowledge of honey's healing properties")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Earnings from honey trading and guiding")
    
  elif agent_name == "carlos_mendez":
    # Carlos: Cuban tobacco farmer and cigar maker
    agent.add_to_inventory("premium_cigars", 15, 1, 85.00, "Hand-rolled premium cigars from Vuelta Abajo tobacco")
    agent.add_to_inventory("wrapper_tobacco_leaves", 25, 1, 35.00, "Premium wrapper tobacco leaves for cigar making")
    agent.add_to_inventory("aged_cigars", 8, 1, 150.00, "Aged cigars with 5+ years of careful humidor storage")
    agent.add_to_inventory("cuban_rum", 6, 1, 75.00, "Authentic Cuban rum for cigar pairing")
    agent.add_to_inventory("aged_whisky", 4, 1, 120.00, "Premium aged whisky for sophisticated cigar sessions")
    agent.add_to_inventory("cigar_humidor", 2, 1, 300.00, "Traditional cedar humidors for proper cigar storage")
    agent.add_to_inventory("tobacco_seeds", 12, 1, 25.00, "Heritage Cuban tobacco seeds from family farm")
    agent.add_to_inventory("rolling_tools", 1, 1, 200.00, "Traditional cigar rolling tools and molds")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Farm earnings and cigar sales")
    
  elif agent_name == "bianca_silva":
    # Bianca: Brazilian pool products entrepreneur
    agent.add_to_inventory("chlorine_tablets", 50, 1, 12.00, "High-quality chlorine tablets for pool sanitization")
    agent.add_to_inventory("ph_balancer", 25, 1, 18.00, "pH balancing chemicals for perfect water chemistry")
    agent.add_to_inventory("pool_vacuum", 3, 1, 180.00, "Professional-grade automatic pool vacuum cleaner")
    agent.add_to_inventory("skimmer_nets", 15, 1, 25.00, "Heavy-duty skimmer nets for debris removal")
    agent.add_to_inventory("pool_brushes", 20, 1, 35.00, "Professional pool brushes for wall and floor cleaning")
    agent.add_to_inventory("algae_treatment", 30, 1, 22.00, "Fast-acting algae killer for crystal clear water")
    agent.add_to_inventory("pool_shock", 40, 1, 15.00, "Super chlorination treatment for problem pools")
    agent.add_to_inventory("water_test_kits", 35, 1, 28.00, "Complete water testing kits for chemical balance monitoring")
    agent.add_to_inventory("pool_floats", 8, 1, 45.00, "Fun inflatable floats perfect for pool parties - flamingos, donuts, and unicorns!")
    agent.add_to_inventory("underwater_lights", 12, 1, 85.00, "LED underwater lights that change colors - perfect for night parties!")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Starting business cash")
    
  elif agent_name == "mei_chen":
    # Mei: Chinese silk clothing designer and entrepreneur
    agent.add_to_inventory("silk_qipao_dress", 8, 1, 280.00, "Handmade traditional qipao dress in authentic mulberry silk with hand-embroidered details")
    agent.add_to_inventory("silk_scarves", 25, 1, 85.00, "Pure silk scarves with traditional Chinese patterns - hand-finished edges")
    agent.add_to_inventory("silk_blouses", 15, 1, 165.00, "Contemporary silk blouses combining traditional techniques with modern cuts")
    agent.add_to_inventory("silk_pajama_sets", 12, 1, 220.00, "Luxurious mulberry silk pajama sets with traditional Chinese knot buttons")
    agent.add_to_inventory("embroidered_silk_shawls", 6, 1, 320.00, "Heirloom-quality silk shawls with intricate hand-embroidered dragons and phoenixes")
    agent.add_to_inventory("silk_business_jackets", 10, 1, 380.00, "Modern business jackets in premium silk with subtle traditional design elements")
    agent.add_to_inventory("raw_silk_fabric", 30, 1, 45.00, "Premium raw silk fabric by the meter - perfect for custom tailoring")
    agent.add_to_inventory("silk_hair_accessories", 40, 1, 35.00, "Delicate silk hair accessories including headbands, scrunchies, and traditional hair pins")
    agent.add_to_inventory("wedding_silk_gowns", 3, 1, 1200.00, "Bespoke wedding gowns combining Western silhouettes with traditional Chinese silk and embroidery")
    agent.add_to_inventory("silk_ties_men", 20, 1, 95.00, "Men's silk ties featuring subtle traditional Chinese motifs for international businessmen")
    agent.add_to_inventory("silk_care_kit", 15, 1, 55.00, "Complete silk care kit with gentle cleaners and preservation instructions in multiple languages")
    agent.add_to_inventory("digital cash", 1000, 1, 1.00, "Starting business cash")

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
  
  # Build Pema
  pema = GenerativeAgent("Synthetic_Base", "pema_sherpa")
  for m in pema_memories:
    pema.remember(m)
  setup_agent_inventory(pema, "pema_sherpa")
  pema.save("Synthetic", "pema_sherpa")
  
  # Build Carlos
  carlos = GenerativeAgent("Synthetic_Base", "carlos_mendez")
  for m in carlos_memories:
    carlos.remember(m)
  setup_agent_inventory(carlos, "carlos_mendez")
  carlos.save("Synthetic", "carlos_mendez")
  
  # Build Bianca
  bianca = GenerativeAgent("Synthetic_Base", "bianca_silva")
  for m in bianca_memories:
    bianca.remember(m)
  setup_agent_inventory(bianca, "bianca_silva")
  bianca.save("Synthetic", "bianca_silva")
  
  # Build Mei
  mei = GenerativeAgent("Synthetic_Base", "mei_chen")
  for m in mei_memories:
    mei.remember(m)
  setup_agent_inventory(mei, "mei_chen")
  mei.save("Synthetic", "mei_chen")
  
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
  agent_names = ["rowan_greenwood", "jasmine_carter", "mina_kim", "kemi_adebayo", "bianca_silva", "mei_chen"]
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


def test_markov_agent_scoring():
  """Test the markov_probs_v1.txt scoring system with agents from previous interactions"""
  print("=== TESTING MARKOV AGENT SCORING SYSTEM ===")
  print()
  
  # Load agents that participated in the Markov chain simulation
  agent_names = ["rowan_greenwood", "jasmine_carter", "mina_kim", "kemi_adebayo", 
                 "pema_sherpa", "carlos_mendez", "bianca_silva", "mei_chen"]
  
  agents = {}
  for agent_name in agent_names:
    try:
      agent = GenerativeAgent("Synthetic", agent_name)
      agents[agent.scratch.get_fullname()] = agent
      print(f"✓ Loaded {agent.scratch.get_fullname()}")
    except Exception as e:
      print(f"✗ Failed to load {agent_name}: {e}")
  
  if len(agents) < 2:
    print("Error: Need at least 2 agents for scoring test")
    return
  
  print(f"\nTesting markov scoring with {len(agents)} agents...")
  print()
  
  # Test scoring for each agent
  for agent_name, agent in agents.items():
    print(f"=== {agent_name.upper()} - BUYING INTEREST SCORES ===")
    
    # Get list of other agents
    other_agents = [name for name in agents.keys() if name != agent_name]
    
    try:
      # Get markov buying interest probability distribution
      probabilities = agent.get_markov_buying_interest_scores(other_agents)
      
      print(f"Political Ideology: {agent.scratch.political_ideology}")
      print(f"Scoring {len(other_agents)} other agents (Temperature = 10.0)...")
      print()
      
      # Display probabilities
      for other_agent, prob in probabilities.items():
        print(f"  {other_agent}: {prob:.3f} ({prob*100:.1f}%)")
      
      # Verify probabilities sum to 1.0
      total_prob = sum(probabilities.values())
      print(f"\nTotal probability: {total_prob:.6f}")
      
      print()
      print("JSON format:")
      import json
      print(json.dumps({"probabilities": probabilities}, indent=2))
      
    except Exception as e:
      print(f"Error getting scores for {agent_name}: {e}")
    
    print("\n" + "-"*50 + "\n")


def main(): 
  # Simplified main for multi-agent Markov chain interactions
  # build_agent()
  interview_agent()
  # chat_with_agent()
  # ask_agent_to_reflect()
  
  # Use the new Markov agent chain system
  #test_markov_chain_simulation(testing_mode=True)
  
  # Test the markov scoring system
  # test_markov_agent_scoring()



if __name__ == '__main__':
  main()
  