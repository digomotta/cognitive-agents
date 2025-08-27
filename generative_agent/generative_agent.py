import json

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

  # def utterance(self, curr_dialogue: List[List[str]], context: str = "", conversation_id: str = "") -> str:
  #   """
  #   Given a dialogue of the form, 
  #     [["Agent 1": "Content..."],
  #      ["Agent 2": "Content..."], ... ]
  #   generate the next agent utterance. 

  #   Parameters:
  #     anchor: str reflection anchor
  #     time_step: int entering timestep
  #   Returns: 
  #     None
  #   """
  #   ret = utterance_conversation_based(self, conversation_id, curr_dialogue, context)
  #   return ret

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

  def has_inventory_item(self, item_name: str, minimum_quantity: int = 1) -> bool:
    """Check if agent has a specific item in sufficient quantity."""
    return self.inventory.has_item(item_name, minimum_quantity)

  def get_trade_history(self, item_name: str = None) -> List[Dict]:
    """Get the agent's trading history, optionally filtered by item."""
    return self.inventory.get_trade_history(item_name) 

  def Act(self, conversation_id: str, curr_dialogue: List[List[str]], context: str = "") -> str:
    """
    Act in the conversation.

    Parameters:
      conversation_id: Unique identifier for this conversation session
      curr_dialogue: List of [speaker, message] pairs
      context: Context for the conversation
    Returns: 
      Generated response string
    """
    return utterance_conversation_based(self, conversation_id, curr_dialogue, context)
