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

  #try:

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
  
  #finally:
    # Always clear working memory when conversation ends
    #print("\n=== Conversation ended. Clearing working memory ===")
    #generative_agent.working_memory.end_interaction()


def setup_agent_inventory(agent, agent_name):
  """Set up initial inventory for an agent and clear history."""
  # Clear existing inventory and records
  agent.inventory.items.clear()
  agent.inventory.records.clear()
  agent.save()  # Save the cleared inventory to JSON files
# Target: 11 product SKUs per agent (excluding digital cash)

  if agent_name == "rowan_greenwood":
      # Rowan: Real estate agent with herbal products
      agent.add_to_inventory("herbal_tea", 5, 1, 15.00, 3.75, "Calming herbal tea blend")
      agent.add_to_inventory("black_tea", 5, 1, 15.00, 3.75, "Energetic black tea")
      agent.add_to_inventory("medicinal_cannabis", 10, 1, 8.50, 2.13, "Medicinal cannabis")
      agent.add_to_inventory("property_contracts", 3, 1, 200.00, 50.00, "Real estate contracts ready to sign")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("cbd_oil", 8, 1, 25.00, 6.25, "Full-spectrum CBD oil")
      agent.add_to_inventory("herbal_salve", 10, 1, 18.00, 4.50, "Soothing herbal salve")
      agent.add_to_inventory("essential_oil_blends", 6, 1, 22.00, 5.50, "Relaxing essential oil blends")
      agent.add_to_inventory("home_staging_kits", 3, 1, 180.00, 45.00, "DIY home staging kit")
      agent.add_to_inventory("virtual_tour_packages", 4, 1, 120.00, 30.00, "360° virtual tour packages")
      agent.add_to_inventory("open_house_signs", 6, 1, 35.00, 8.75, "Reusable open house sign set")
      agent.add_to_inventory("reusable_tea_infusers", 12, 1, 8.00, 2.00, "Stainless steel tea infusers")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Starting business cash")

  elif agent_name == "jasmine_carter":
      # Jasmine: Math student with academic supplies
      agent.add_to_inventory("textbooks", 4, 1, 85.00, 21.25, "Advanced mathematics textbooks")
      agent.add_to_inventory("graphing_calculator", 1, 1, 120.00, 30.00, "TI-84 Plus calculator")
      agent.add_to_inventory("notebooks", 8, 1, 3.50, 0.88, "High-quality notebooks")
      agent.add_to_inventory("tutoring_sessions", 2, 1, 40.00, 10.00, "One-hour math tutoring sessions")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("mechanical_pencils", 12, 1, 2.50, 0.63, "0.5mm mechanical pencils")
      agent.add_to_inventory("gel_pens", 10, 1, 3.00, 0.75, "Smooth gel pens")
      agent.add_to_inventory("whiteboard_markers", 5, 1, 9.00, 2.25, "Low-odor whiteboard markers")
      agent.add_to_inventory("study_guides", 5, 1, 25.00, 6.25, "Curated exam study guides")
      agent.add_to_inventory("online_course_vouchers", 2, 1, 60.00, 15.00, "Access to online math courses")
      agent.add_to_inventory("math_software_license", 3, 1, 45.00, 11.25, "CAS/linear algebra software license")
      agent.add_to_inventory("ruler_set", 5, 1, 6.00, 1.50, "Metric/imperial ruler & protractor set")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Student savings")

  elif agent_name == "mina_kim":
      # Mina: Korean beauty cosmetics expert
      agent.add_to_inventory("sheet_masks", 20, 1, 3.50, 0.88, "Korean sheet masks - various types")
      agent.add_to_inventory("essence", 5, 1, 28.00, 7.00, "Korean essence serums")
      agent.add_to_inventory("cushion_foundation", 3, 1, 35.00, 8.75, "BB cushion foundations")
      agent.add_to_inventory("lip_tints", 8, 1, 12.00, 3.00, "Korean gradient lip tints")
      agent.add_to_inventory("sunscreen", 4, 1, 22.00, 5.50, "Korean SPF50+ sunscreens")
      agent.add_to_inventory("sleeping_masks", 6, 1, 18.00, 4.50, "Overnight sleeping masks")
      agent.add_to_inventory("cleansing_oil", 3, 1, 25.00, 6.25, "Double cleansing oils")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("toner", 6, 1, 20.00, 5.00, "Hydrating, low-pH toner")
      agent.add_to_inventory("ampoule_serums", 4, 1, 32.00, 8.00, "Concentrated ampoule serums")
      agent.add_to_inventory("eye_cream", 4, 1, 26.00, 6.50, "Brightening eye cream")
      agent.add_to_inventory("gel_moisturizer", 5, 1, 24.00, 6.00, "Lightweight gel moisturizer")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "K-beauty business earnings")

  elif agent_name == "kemi_adebayo":
      # Kemi: Nigerian tech entrepreneur with African superfood products
      agent.add_to_inventory("moringa_powder", 15, 1, 45.00, 11.25, "High-protein moringa superfood powder")
      agent.add_to_inventory("baobab_fruit_powder", 10, 1, 55.00, 13.75, "Vitamin C rich baobab powder")
      agent.add_to_inventory("hibiscus_extract", 8, 1, 35.00, 8.75, "Antioxidant hibiscus extract capsules")
      agent.add_to_inventory("tiger_nut_flour", 12, 1, 25.00, 6.25, "Gluten-free tiger nut flour")
      agent.add_to_inventory("african_yam_chips", 20, 1, 18.00, 4.50, "Dehydrated nutrient-dense yam chips")
      agent.add_to_inventory("palm_fruit_oil", 6, 1, 40.00, 10.00, "Unprocessed red palm oil")
      agent.add_to_inventory("research_reports", 3, 1, 200.00, 50.00, "Proprietary food tech research and patents")
      agent.add_to_inventory("mobile_app_licenses", 2, 1, 500.00, 125.00, "Nutrition education app licenses")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("shea_butter", 12, 1, 20.00, 5.00, "Unrefined West African shea butter")
      agent.add_to_inventory("fonio_grain", 15, 1, 35.00, 8.75, "Ancient whole grain fonio")
      agent.add_to_inventory("dried_hibiscus_petals", 10, 1, 18.00, 4.50, "Zobo/karkadé hibiscus petals")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Startup revenue and investment funds")

  elif agent_name == "pema_sherpa":
      # Pema: Nepalese honey hunter with wild and mad honey
      agent.add_to_inventory("mad_honey", 3, 1, 150.00, 37.50, "Sacred psychoactive honey from high-altitude rhododendron nectar")
      agent.add_to_inventory("wild_cliff_honey", 8, 1, 80.00, 20.00, "Raw honey harvested from giant bee colonies on cliff faces")
      agent.add_to_inventory("mountain_flower_honey", 12, 1, 45.00, 11.25, "Wildflower honey from high Himalayan meadows")
      agent.add_to_inventory("pine_honey", 6, 1, 55.00, 13.75, "Dark honey with medicinal properties from pine tree secretions")
      agent.add_to_inventory("prayer_blessed_honey", 4, 1, 120.00, 30.00, "Ceremonially blessed honey for spiritual and healing purposes")
      agent.add_to_inventory("traditional_climbing_gear", 2, 1, 300.00, 75.00, "Handmade rope ladders and collection tools")
      agent.add_to_inventory("honey_medicinal_guide", 1, 1, 200.00, 50.00, "Ancient family knowledge of honey's healing properties")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("beeswax_blocks", 10, 1, 12.00, 3.00, "Pure beeswax blocks for crafts")
      agent.add_to_inventory("propolis_tincture", 6, 1, 45.00, 11.25, "Antimicrobial propolis tincture")
      agent.add_to_inventory("honeycomb_wedges", 12, 1, 25.00, 6.25, "Raw honeycomb pieces")
      agent.add_to_inventory("smoker_kit", 2, 1, 85.00, 21.25, "Traditional bee smoker & tools kit")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Earnings from honey trading and guiding")

  elif agent_name == "carlos_mendez":
      # Carlos: Cuban tobacco farmer and cigar maker
      agent.add_to_inventory("premium_cigars", 15, 1, 85.00, 21.25, "Hand-rolled premium cigars from Vuelta Abajo tobacco")
      agent.add_to_inventory("wrapper_tobacco_leaves", 25, 1, 35.00, 8.75, "Premium wrapper tobacco leaves for cigar making")
      agent.add_to_inventory("aged_cigars", 8, 1, 150.00, 37.50, "Aged cigars with 5+ years of careful humidor storage")
      agent.add_to_inventory("cuban_rum", 6, 1, 75.00, 18.75, "Authentic Cuban rum for cigar pairing")
      agent.add_to_inventory("aged_whisky", 4, 1, 120.00, 30.00, "Premium aged whisky for sophisticated cigar sessions")
      agent.add_to_inventory("cigar_humidor", 2, 1, 300.00, 75.00, "Traditional cedar humidors for proper cigar storage")
      agent.add_to_inventory("tobacco_seeds", 12, 1, 25.00, 6.25, "Heritage Cuban tobacco seeds from family farm")
      agent.add_to_inventory("rolling_tools", 1, 1, 200.00, 50.00, "Traditional cigar rolling tools and molds")
      # Additions to reach 11 SKUs
      agent.add_to_inventory("cigar_cutters", 10, 1, 30.00, 7.50, "Guillotine and V-cut cigar cutters")
      agent.add_to_inventory("butane_torch_lighters", 8, 1, 40.00, 10.00, "Refillable torch lighters")
      agent.add_to_inventory("humidor_solution", 12, 1, 15.00, 3.75, "Propylene glycol humidification solution")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Farm earnings and cigar sales")

  elif agent_name == "bianca_silva":
      # Bianca: Brazilian pool products entrepreneur
      agent.add_to_inventory("chlorine_tablets", 50, 1, 12.00, 3.00, "High-quality chlorine tablets for pool sanitization")
      agent.add_to_inventory("ph_balancer", 25, 1, 18.00, 4.50, "pH balancing chemicals for perfect water chemistry")
      agent.add_to_inventory("pool_vacuum", 3, 1, 180.00, 45.00, "Professional-grade automatic pool vacuum cleaner")
      agent.add_to_inventory("skimmer_nets", 15, 1, 25.00, 6.25, "Heavy-duty skimmer nets for debris removal")
      agent.add_to_inventory("pool_brushes", 20, 1, 35.00, 8.75, "Professional pool brushes for wall and floor cleaning")
      agent.add_to_inventory("algae_treatment", 30, 1, 22.00, 5.50, "Fast-acting algae killer for crystal clear water")
      agent.add_to_inventory("pool_shock", 40, 1, 15.00, 3.75, "Super chlorination treatment for problem pools")
      agent.add_to_inventory("water_test_kits", 35, 1, 28.00, 7.00, "Complete water testing kits for chemical balance monitoring")
      agent.add_to_inventory("pool_floats", 8, 1, 45.00, 11.25, "Fun inflatable floats perfect for pool parties - flamingos, donuts, and unicorns!")
      agent.add_to_inventory("underwater_lights", 12, 1, 85.00, 21.25, "LED underwater lights that change colors - perfect for night parties!")
      # Addition to reach 11 SKUs
      agent.add_to_inventory("filter_cartridges", 20, 1, 32.00, 8.00, "Replacement filter cartridges for common systems")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Starting business cash")

  elif agent_name == "mei_chen":
      # Mei: Chinese silk clothing designer and entrepreneur (already at 11 SKUs)
      agent.add_to_inventory("silk_qipao_dress", 8, 1, 280.00, 70.00, "Handmade traditional qipao dress in authentic mulberry silk with hand-embroidered details")
      agent.add_to_inventory("silk_scarves", 25, 1, 85.00, 21.25, "Pure silk scarves with traditional Chinese patterns - hand-finished edges")
      agent.add_to_inventory("silk_blouses", 15, 1, 165.00, 41.25, "Contemporary silk blouses combining traditional techniques with modern cuts")
      agent.add_to_inventory("silk_pajama_sets", 12, 1, 220.00, 55.00, "Luxurious mulberry silk pajama sets with traditional Chinese knot buttons")
      agent.add_to_inventory("embroidered_silk_shawls", 6, 1, 320.00, 80.00, "Heirloom-quality silk shawls with intricate hand-embroidered dragons and phoenixes")
      agent.add_to_inventory("silk_business_jackets", 10, 1, 380.00, 95.00, "Modern business jackets in premium silk with subtle traditional design elements")
      agent.add_to_inventory("raw_silk_fabric", 30, 1, 45.00, 11.25, "Premium raw silk fabric by the meter - perfect for custom tailoring")
      agent.add_to_inventory("silk_hair_accessories", 40, 1, 35.00, 8.75, "Delicate silk hair accessories including headbands, scrunchies, and traditional hair pins")
      agent.add_to_inventory("wedding_silk_gowns", 3, 1, 1200.00, 300.00, "Bespoke wedding gowns combining Western silhouettes with traditional Chinese silk and embroidery")
      agent.add_to_inventory("silk_ties_men", 20, 1, 95.00, 23.75, "Men's silk ties featuring subtle traditional Chinese motifs for international businessmen")
      agent.add_to_inventory("silk_care_kit", 15, 1, 55.00, 13.75, "Complete silk care kit with gentle cleaners and preservation instructions in multiple languages")
      agent.add_to_inventory("digital cash", 1000, 1, 1.00, 0.00, "Starting business cash")

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


def agent_production_planning():
  """Demo of agent production planning functionality."""
  curr_agent = GenerativeAgent("Synthetic", "mei_chen")

  print(f"=== Production Planning Demo for {curr_agent.scratch.get_fullname()} ===")

  # Show current financial status
  available_cash = curr_agent.get_inventory_quantity("digital cash")
  current_inventory = curr_agent.inventory.get_all_items_with_values().get("silk_pajama_sets", {})
  current_quantity = current_inventory.get("quantity", 0)
  production_cost = current_inventory.get("production_cost_per_unit", 0.0)

  print(f"Current status:")
  print(f"  Available cash: ${available_cash:.2f}")
  print(f"  Current silk_scarves inventory: {current_quantity} units")
  print(f"  Production cost per unit: ${production_cost:.2f}")
  print()

  # Create a production plan
  print("Creating production plan...")
  plan_dict = curr_agent.create_production_plan("silk_pajama_sets", time_step=0)
  if plan_dict:
    print(f"Plan created: {plan_dict['planned_quantity']} units to produce")
    print(f"Reasoning: {plan_dict['reasoning'][:100]}...")
    print()

    # Convert dict to ProductionPlan object and execute
    from generative_agent.modules.cognitive.plan import ProductionPlan
    plan_to_execute = ProductionPlan(plan_dict)

    # Execute the production plan
    print("Executing production plan...")
    success = curr_agent.execute_production_plan(plan_to_execute, time_step=1)

    if success:
      # Show updated status
      new_cash = curr_agent.get_inventory_quantity("digital cash")
      new_inventory = curr_agent.inventory.get_all_items_with_values().get("herbal_tea", {})
      new_quantity = new_inventory.get("quantity", 0)

      print(f"Production completed!")
      print(f"  Cash after production: ${new_cash:.2f} (spent: ${available_cash - new_cash:.2f})")
      print(f"  New herbal_tea inventory: {new_quantity} units (added: {new_quantity - current_quantity})")
    else:
      print("Production failed!")
  else:
    print("Failed to create production plan")

  curr_agent.save()

def smart_production_planning():
  """Demo of smart production planning based on recent sales."""
  curr_agent = GenerativeAgent("Synthetic", "mei_chen")

  print(f"=== Smart Production Planning Demo for {curr_agent.scratch.get_fullname()} ===")

  # Show current financial status
  available_cash = curr_agent.get_inventory_quantity("digital cash")
  print(f"Available cash: ${available_cash:.2f}")
  print()

  # Get items to produce based on recent sales
  print("Analyzing recent sales to determine what to produce...")
  items_to_produce = curr_agent.get_items_to_produce_from_sales(max_items=5)

  if not items_to_produce:
    print("No recent sales found. Cannot determine what to produce.")
    return

  print(f"Found {len(items_to_produce)} items from recent sales:")
  for i, item in enumerate(items_to_produce, 1):
    current_inventory = curr_agent.inventory.get_all_items_with_values().get(item, {})
    current_quantity = current_inventory.get("quantity", 0)
    production_cost = current_inventory.get("production_cost_per_unit", 0.0)
    print(f"  {i}. {item}: {current_quantity} units, ${production_cost:.2f}/unit production cost")
  print()

  # Create production plans for all items
  print("Creating production plans for recent sales items...")
  plans = curr_agent.create_production_plans_for_recent_sales(time_step=0, max_items=5)

  if plans:
    print(f"\n✓ Created {len(plans)} production plans")

    # Show total planned production cost
    total_cost = 0
    for plan in plans:
      item_name = plan['item_name']
      quantity = plan['planned_quantity']
      current_inventory = curr_agent.inventory.get_all_items_with_values().get(item_name, {})
      production_cost = current_inventory.get("production_cost_per_unit", 0.0)
      item_cost = quantity * production_cost
      total_cost += item_cost
      print(f"  {item_name}: {quantity} units (${item_cost:.2f})")

    print(f"Total planned production cost: ${total_cost:.2f}")
    print(f"Remaining cash after production: ${available_cash - total_cost:.2f}")
  else:
    print("No production plans were created.")

  curr_agent.save()

def create_sample_sales_data():
  """Create some sample sales transactions for Rowan to test sales history."""
  curr_agent = GenerativeAgent("Synthetic", "rowan_greenwood")

  print(f"Creating sample sales data for {curr_agent.scratch.get_fullname()}...")

  # Create some sample sales transactions
  curr_agent.sell_item("herbal_tea", 2, 2, buyer="Local Cafe", price_per_unit=15.00, description="Sold to local cafe for their morning blend")
  curr_agent.sell_item("herbal_tea", 3, 3, buyer="Jasmine Carter", price_per_unit=16.00, description="Sold to regular customer at market")
  curr_agent.sell_item("herbal_tea", 1, 4, buyer="Mei Chen", price_per_unit=15.50, description="Sold during market day")
  curr_agent.sell_item("black_tea", 2, 5, buyer="Carlos Mendez", price_per_unit=15.00, description="Trade at weekend market")
  curr_agent.sell_item("cbd_oil", 1, 6, buyer="Pema Sherpa", price_per_unit=25.00, description="Sold for wellness purposes")

  print("Sample sales created!")
  curr_agent.save()
  return curr_agent

def sales_history():
  curr_agent = GenerativeAgent("Synthetic", "rowan_greenwood")

  print("=== Sales History for herbal_tea ===")
  herbal_tea_sales = curr_agent.get_sales_history("herbal_tea")
  print(f"Number of herbal_tea sales: {len(herbal_tea_sales)}")
  for sale in herbal_tea_sales:
    print(f"  Sold {sale['quantity']} units to {sale['trade_partner']} at time {sale['time_step']}")

  print("\n=== All Sales History ===")
  all_sales = curr_agent.get_sales_history()
  print(f"Total number of sales: {len(all_sales)}")
  for sale in all_sales:
    print(f"  {sale['item_name']}: {sale['quantity']} units to {sale['trade_partner']} at time {sale['time_step']}")

  return curr_agent

def main(): 
  # Simplified main for multi-agent Markov chain interactions
  # build_agent()
  # interview_agent()
  # chat_with_agent()
  #agent_production_planning()
  smart_production_planning()

  # First create some sample sales data, then show the sales history
  #create_sample_sales_data()
  #print("\n" + "="*50 + "\n")
  #sales_history()
  # ask_agent_to_reflect()
  
  # Use the new Markov agent chain system
  #test_markov_chain_simulation(testing_mode=True)
  
  # Test the markov scoring system
  # test_markov_agent_scoring()



if __name__ == '__main__':
  main()
  