import json
import os

from typing import Dict, List, Optional, Union

from generative_agent.modules.cognitive.memory_stream import MemoryStream
from generative_agent.modules.cognitive.scratch import Scratch
from generative_agent.modules.cognitive.inventory import Inventory
from generative_agent.modules.cognitive.working_memory import WorkingMemory
from generative_agent.modules.conversation_interaction import utterance_conversation_based
from simulation_engine.settings import *
from simulation_engine.global_methods import *

# ############################################################################
# ###                        GENERATIVE AGENT CLASS                        ###
# ############################################################################

class GenerativeAgent: 
  def __init__(self, population: str, agent_id: str):
    self.population: str
    self.id: str
    self.forked_population: str
    self.forked_id: str
    self.scratch: Scratch
    self.memory_stream: MemoryStream
    self.inventory: Inventory
    self.working_memory: WorkingMemory

    # The location of the population folder for the agent. 
    agent_folder = f"{POPULATIONS_DIR}/{population}/{agent_id}"

    # We stop the process if the agent storage folder already exists. 
    if not check_if_file_exists(f"{agent_folder}/scratch.json"):
      print ("Generative agent does not exist in the current location.")
      return 
    
    # Loading the agent's memories. 
    with open(f"{agent_folder}/meta.json") as json_file:
      meta = json.load(json_file)
    with open(f"{agent_folder}/scratch.json") as json_file:
      scratch = json.load(json_file)
    with open(f"{agent_folder}/memory_stream/embeddings.json") as json_file:
      embeddings = json.load(json_file)
    with open(f"{agent_folder}/memory_stream/nodes.json") as json_file:
      nodes = json.load(json_file)
    
    # Loading inventory data
    inventory_data = {"items": [], "records": []}
    if check_if_file_exists(f"{agent_folder}/inventory.json"):
      with open(f"{agent_folder}/inventory.json") as json_file:
        inventory_data = json.load(json_file)

    self.population = meta["population"] 
    self.id = meta["id"] 
    self.forked_population = meta["population"] 
    self.forked_id = meta["id"]
    self.scratch = Scratch(scratch)
    self.memory_stream = MemoryStream(nodes, embeddings)
    self.inventory = Inventory(inventory_data.get("items", []), inventory_data.get("records", []))
    self.working_memory = WorkingMemory()
    
    print (f"Loaded {agent_id}:{population}")

  def initialize(self, population: str, agent_id: str) -> None: 
    """
    Initializes the agent storage folder and its components files init. The 
    folder that is created contains everything that a generative agent needs
    to contain, from its memory stream to scratch memory.  

    Parameters:
      population: The current population.
      agent_id: The id of the agent.
    Returns: 
      None
    """
    # The location of the population folder for the agent. 
    agent_folder = f"{POPULATIONS_DIR}/{population}/{agent_id}"

    # We stop the process if the agent storage folder already exists. 
    if check_if_file_exists(f"{agent_folder}/meta.json"):
      print ("Init not run as the agent storage folder already exists")

    else: 
      # Creating the agent storage folder.
      print (f"Initializing {agent_id}:{population}'s agent storage.")
      create_folder_if_not_there(agent_folder)
      print (f"-- Created {agent_folder}")
      create_folder_if_not_there(f"{agent_folder}/memory_stream")
      print (f"-- Created {agent_folder}/memory_stream")

      # Initializing meta file
      with open(f"{agent_folder}/meta.json", "w") as file:
        meta = {"population": population, 
                "id": agent_id,
                "forked_population": population,
                "forked_id": agent_id}
        json.dump(meta, file, indent=2)  

      # Initializing scratch
      with open(f"{agent_folder}/scratch.json", "w") as file:
        scratch = Scratch().package()
        json.dump(scratch, file, indent=2)  

      # Initializing embeddings
      with open(f"{agent_folder}/memory_stream/embeddings.json", "w") as file:
        json.dump({}, file, indent=2)  

      # Initializing nodes
      with open(f"{agent_folder}/memory_stream/nodes.json", "w") as file:
        json.dump([], file, indent=2)      

      # Initializing inventory
      with open(f"{agent_folder}/inventory.json", "w") as file:
        json.dump({"items": [], "records": []}, file, indent=2)

    # Initialize with empty data
    self.population = population
    self.id = agent_id
    self.forked_population = population
    self.forked_id = agent_id
    self.scratch = Scratch()
    self.memory_stream = MemoryStream([], {})
    self.inventory = Inventory([], [])
    self.working_memory = WorkingMemory()

  def package(self): 
    """
    Packaging the agent's meta info for saving. 

    Parameters:
      None
    Returns: 
      packaged dictionary
    """
    return {"population": self.population,
            "id": self.id,
            "forked_population": self.forked_population,
            "forked_id": self.forked_id}

  def save(self, save_population=None, save_id=None): 
    """
    Given a save_code, save the agents' state in the storage. Right now, the 
    save directory works as follows: 
    'storage/<agent_name>/<save_code>'

    As you grow different versions of the agent, save the new agent state in 
    a different save code location. Remember that 'init' is the originally
    initialized agent directory.

    Parameters:
      save_code: str
    Returns: 
      None
    """
    if not save_population: 
      save_population = self.population
    if not save_id: 
      save_id = self.id

    self.forked_population = self.population
    self.forked_id = self.id
    self.population = save_population
    self.id = save_id

    # Name of the agent and the current save location. 
    storage = f"{POPULATIONS_DIR}/{save_population}/{save_id}"
    create_folder_if_not_there(storage)
    create_folder_if_not_there(f"{storage}/memory_stream")
    
    # Saving the agent's memory stream. This includes saving the embeddings 
    # as well as the nodes. 
    with open(f"{storage}/memory_stream/embeddings.json", "w") as json_file:
      json.dump(self.memory_stream.embeddings, 
                json_file)
    with open(f"{storage}/memory_stream/nodes.json", "w") as json_file:
      json.dump([node.package() for node in self.memory_stream.seq_nodes], 
                json_file, indent=2)

    # Saving the agent's scratch memories. 
    with open(f"{storage}/scratch.json", "w") as json_file:
      agent_scratch_summary = self.scratch.package()
      json.dump(agent_scratch_summary, json_file, indent=2)

    # Saving the agent's inventory.
    with open(f"{storage}/inventory.json", "w") as json_file:
      inventory_summary = self.inventory.package()
      json.dump(inventory_summary, json_file, indent=2)

    # Saving the agent's meta information. 
    with open(f"{storage}/meta.json", "w") as json_file:
      agent_meta_summary = self.package()
      json.dump(agent_meta_summary, json_file, indent=2)

  def remember(self, content: str, time_step: int = 0) -> None: 
    """
    Add a new observation to the memory stream. 

    Parameters:
      content: The content of the current memory record that we are adding to
        the agent's memory stream. 
    Returns: 
      None
    """
    self.memory_stream.remember(content, time_step)

  def reflect(self, anchor: str, time_step: int = 0) -> None: 
    """
    Add a new reflection to the memory stream. 

    Parameters:
      anchor: str reflection anchor
      time_step: int entering timestep
    Returns: 
      None
    """
    self.memory_stream.reflect(anchor, time_step)

  def add_to_inventory(self, item_name: str, quantity: int, time_step: int = 0, value: float = 0.0, description: str = "") -> None:
    """Add items to the agent's inventory."""
    self.inventory.add_item(item_name, quantity, time_step, value, description)

  def remove_from_inventory(self, item_name: str, quantity: int, time_step: int = 0, description: str = "") -> bool:
    """Remove items from the agent's inventory. Returns True if successful."""
    return self.inventory.remove_item(item_name, quantity, time_step, description)

  def trade_inventory_item(self, item_name: str, quantity: int, is_giving: bool, 
                          trade_partner: str, time_step: int = 0, value: float = 0.0, description: str = "") -> bool:
    """Trade items with another agent. Returns True if successful."""
    return self.inventory.trade_item(item_name, quantity, is_giving, time_step, trade_partner, value, description)

  def get_inventory_quantity(self, item_name: str) -> int:
    """Get the quantity of a specific item in inventory."""
    return self.inventory.get_item_quantity(item_name)

  def get_inventory_value(self, item_name: str) -> float:
    """Get the value per unit of a specific item in inventory."""
    return self.inventory.get_item_value(item_name)

  def get_inventory_total_value(self, item_name: str) -> float:
    """Get the total value of all units of a specific item in inventory."""
    return self.inventory.get_item_total_value(item_name)

  def get_total_inventory_value(self) -> float:
    """Get the total value of the entire inventory."""
    return self.inventory.get_total_inventory_value()

  def get_all_items_with_values(self) -> Dict[str, float]:
    """Get the inventory items and their values."""
    return self.inventory.get_all_items_with_values()

  def has_inventory_item(self, item_name: str, minimum_quantity: int = 1) -> bool:
    """Check if agent has a specific item in sufficient quantity."""
    return self.inventory.has_item(item_name, minimum_quantity)

  def get_trade_history(self, item_name: str = None) -> List[Dict]:
    """Get the agent's trading history, optionally filtered by item."""
    return self.inventory.get_trade_history(item_name) 

  def receive_payment(self, payment_amount: float, time_step: int = 0, payer: str = "", description: str = "") -> bool:
    """Record receiving payment (typically digital cash)."""
    return self.inventory.receive_payment(payment_amount, time_step, payer, description)

  def sell_item(self, item_name: str, quantity: int, time_step: int = 0, buyer: str = "", price_per_unit: float = 0.0, description: str = "") -> bool:
    """Record selling an item (removes from inventory and optionally records payment)."""
    return self.inventory.sell_item(item_name, quantity, time_step, buyer, price_per_unit, description)

  def make_payment(self, payment_amount: float, time_step: int = 0, recipient: str = "", description: str = "") -> bool:
    """Record making a payment (removes digital cash from inventory)."""
    return self.inventory.make_payment(payment_amount, time_step, recipient, description)

  def buy_item(self, item_name: str, quantity: int, time_step: int = 0, seller: str = "", price_per_unit: float = 0.0, description: str = "") -> bool:
    """Record buying an item (adds to inventory and optionally makes payment)."""
    return self.inventory.buy_item(item_name, quantity, time_step, seller, price_per_unit, description)

  def get_payment_history(self, item_name: str = None) -> List[Dict]:
    """Get the agent's payment history (both made and received)."""
    return self.inventory.get_payment_history(item_name)

  def get_sales_history(self, item_name: str = None) -> List[Dict]:
    """Get the agent's sales transaction history."""
    return self.inventory.get_sales_history(item_name)

  def get_purchase_history(self, item_name: str = None) -> List[Dict]:
    """Get the agent's purchase transaction history."""
    return self.inventory.get_purchase_history(item_name)

  def get_transaction_summary(self) -> Dict[str, int]:
    """Get a summary count of all transaction types."""
    return self.inventory.get_transaction_summary()

  def get_markov_buying_interest_scores(self, other_agents: List[str], temperature: float = 10.0) -> Dict[str, float]:
    """
    Apply markov_probs_v1.txt scoring system to evaluate buying interest in other agents.
    Returns a probability distribution using softmax.
    
    Parameters:
      other_agents: List of other agent names to score
      temperature: Temperature parameter for softmax (higher = more uniform, lower = more peaked)
    Returns:
      Dict mapping agent names to probabilities (sum to 1.0)
    """
    from simulation_engine.gpt_structure import gpt_request
    import math
    import json
    
    # Get agent persona information
    persona_info = f"{self.scratch.get_fullname()}\n"
    persona_info += f"Age: {self.scratch.age}\n" 
    persona_info += f"Political Ideology: {self.scratch.political_ideology}\n"
    persona_info += f"Self Description: {self.scratch.self_description}\n"
    persona_info += f"Fact Sheet: {self.scratch.fact_sheet}\n"
    
    # Load the markov probability prompt template
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_path = os.path.join(
      project_root,
      "simulation_engine",
      "prompt_template",
      "generative_agent",
      "interaction",
      "utternace",
      "markov_probs_v1.txt",
    )
    with open(template_path, "r") as f:
      prompt_template = f.read()
    
    # Evaluate each agent one at a time
    raw_scores = {}
    
    for agent_name in other_agents:
      # Get relevant memories about this specific agent
      retrieved_memories = self.memory_stream.retrieve([agent_name], 0, n_count=5)
      
      if agent_name in retrieved_memories and retrieved_memories[agent_name]:
        memories_text = "\n".join([f"Memory: {mem.content}" for mem in retrieved_memories[agent_name]])
      else:
        memories_text = "No specific memories about this character."
              
      # Format the prompt for this specific agent
      prompt = prompt_template.replace("!<INPUT 0>!", persona_info)
      prompt = prompt.replace("!<INPUT 1>!", agent_name)
      prompt = prompt.replace("!<INPUT 2>!", memories_text)
      
      # Get response from LLM for this agent
      try:
        response = gpt_request(prompt)
        
        # Parse JSON response
        score_data = json.loads(response)
        raw_scores[agent_name] = score_data.get("score", 50)  # Default to neutral if missing
        
      except Exception as e:
        print(f"Error getting score for {agent_name} from {self.scratch.get_fullname()}: {e}")
        raw_scores[agent_name] = 50  # Neutral fallback
    
    # Apply softmax to convert scores to probability distribution
    # First normalize scores to reduce extreme differences
    scores_list = list(raw_scores.values())
    mean_score = sum(scores_list) / len(scores_list)
    
    # Center scores around mean to reduce variance
    centered_scores = {}
    for agent, score in raw_scores.items():
      centered_scores[agent] = score - mean_score
    
    # Apply softmax with temperature scaling
    exp_scores = {}
    for agent, centered_score in centered_scores.items():
      exp_scores[agent] = math.exp(centered_score / temperature)
    
    # Calculate sum for normalization
    total_exp = sum(exp_scores.values())
    
    # Convert to probabilities
    probabilities = {}
    for agent, exp_score in exp_scores.items():
      probabilities[agent] = exp_score / total_exp
    
    return probabilities

  def Act(self, conversation_id: str, curr_dialogue: List[List[str]], context: str = "", time_step: int = 0) -> str:
    """
    Act in the conversation.

    Parameters:
      conversation_id: Unique identifier for this conversation session
      curr_dialogue: List of [speaker, message] pairs
      context: Context for the conversation
    Returns: 
      Generated response string
    """
    return utterance_conversation_based(self, conversation_id, curr_dialogue, context, time_step)
