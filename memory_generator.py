import json
import os
from simulation_engine.gpt_structure import gpt_request
from simulation_engine.settings import LLM_VERS
from generative_agent.generative_agent import GenerativeAgent


def generate_agent_memories_from_text(agent_name, population_name, text_file_name, output_file_path=None):
    """
    Generate comprehensive agent memories by combining scratch data with text input using LLM augmentation.

    Args:
        agent_name (str): The agent's identifier (e.g., "bianca_silva")
        population_name (str): The population name (e.g., "Synthetic_Base")
        text_file_path (str): Path to .txt file containing memory content to be augmented
        output_file_path (str): Optional path for output file. If None, saves to testing/memories/{agent_name}_memories.py

    Returns:
        str: Path to the generated memory file
    """

    # Load agent's scratch data
    scratch_path = f"agent_bank/populations/{population_name}/{agent_name}/scratch.json"
    text_file_path = f"agent_bank/populations/{population_name}/{agent_name}/{text_file_name}"
    if not os.path.exists(scratch_path):
        raise FileNotFoundError(f"Scratch file not found: {scratch_path}")

    with open(scratch_path, 'r') as f:
        scratch_data = json.load(f)

    # Read the text input file
    if not os.path.exists(text_file_path):
        raise FileNotFoundError(f"Text file not found: {text_file_path}")

    with open(text_file_path, 'r') as f:
        input_text = f.read().strip()

    # Create comprehensive LLM prompt using all scratch data
    prompt = f"""You are creating comprehensive memories for an AI agent. Using the complete agent profile below and the provided text, generate three categories of memories in Python list format.

COMPLETE AGENT PROFILE:
Name: {scratch_data['first_name']} {scratch_data['last_name']}
Age: {scratch_data['age']}
Sex: {scratch_data['sex']}
Location: {scratch_data['address']}
Census Division: {scratch_data['census_division']}
Education: {scratch_data['education']}
Race: {scratch_data['race']}
Ethnicity: {scratch_data['ethnicity']}

Political Views:
- Ideology: {scratch_data['political_ideology']}
- Party: {scratch_data['political_party']}

Personality Traits (Big Five Scale 1-5):
- Extraversion: {scratch_data['extraversion']}
- Agreeableness: {scratch_data['agreeableness']}
- Conscientiousness: {scratch_data['conscientiousness']}
- Neuroticism: {scratch_data['neuroticism']}
- Openness: {scratch_data['openness']}

Background & Work: {scratch_data['fact_sheet']}

Speech Pattern: {scratch_data['speech_pattern']}

Public Self-Description: {scratch_data['self_description']}

Private Self-Description: {scratch_data['private_self_description']}

Sales Performance:
- Total Sales Failures: {scratch_data.get('total_sales_failures', 0)}
- Last Sales Failure Time: {scratch_data.get('last_sales_failure_time', 0)}

INPUT TEXT TO AUGMENT:
{input_text}

Generate exactly 3 Python lists with 15 memories each (45 total):

1. CORE MEMORIES (core = []): Foundational life experiences, major formative events, key relationships, defining moments that shaped who they are. Include childhood experiences, family background, cultural influences, major life decisions, and character-defining moments. Use their personality traits, cultural background, and formative experiences.

2. MUNDANE MEMORIES (mundane = []): Daily routine activities, regular habits, typical interactions, everyday moments. Include morning routines, regular social interactions, shopping habits, leisure activities, and typical day-to-day experiences. Reflect their extraversion level, conscientiousness, and lifestyle.

3. OCCUPATION MEMORIES (occupation = []): Work-related experiences, professional skills, career milestones, job-specific activities. Include client interactions, professional challenges, skill development, workplace relationships, and career growth. Consider their education, conscientiousness, and professional background.

IMPORTANT REQUIREMENTS:
- Each memory should be a complete sentence in past tense, written as a direct statement about what happened
- Write memories as natural narrative statements (e.g., "Sarah discovered her love for baking when she accidentally created the perfect chocolate chip cookie at age twelve.")
- DO NOT start memories with phrases like "He remembered", "She recalled", "The agent thought about", etc.
- Memories should be specific and vivid, not generic
- Include sensory details and emotional context
- Maintain consistency with ALL aspects of the agent's profile
- Incorporate elements from the input text but expand them creatively using the full profile
- Reflect their personality traits in the memories (high extraversion = more social memories, etc.)
- Include cultural and location-specific details from their background
- Show their speech patterns and values through actions and thoughts in memories
- Each list should have exactly 15 memories
- Use their private self-description to add depth and internal conflicts

MEMORY FORMAT EXAMPLES:
Good: "Maria learned to make empanadas from her grandmother during long summer afternoons in Buenos Aires."
Bad: "Maria remembered learning to make empanadas from her grandmother."

Good: "The first time James performed on stage, his hands shook so badly he could barely hold his guitar."
Bad: "James recalled the first time he performed on stage."

Output format should be valid Python code with proper list syntax and the final line:
{agent_name.lower().replace(' ', '_')}_memories = core + mundane + occupation"""

    # Generate memories using LLM
    try:
        generated_content = gpt_request(prompt, model=LLM_VERS, temperature=0.8, max_tokens=4000)
    except Exception as e:
        raise Exception(f"LLM generation failed: {str(e)}")

    # Set default output path if not provided
    if output_file_path is None:
        os.makedirs("testing/memories", exist_ok=True)
        output_file_path = f"testing/memories/{agent_name}_memories.py"

    # Save the generated memories
    with open(output_file_path, 'w') as f:
        f.write(generated_content)

    # Create agent directory structure in both Synthetic_Base and Synthetic populations
    create_agent_structure(agent_name, scratch_data)

    print(f"Generated memories saved to: {output_file_path}")
    print(f"Created agent structure for {agent_name} in Synthetic_Base and Synthetic populations")
    return output_file_path


def create_agent_structure(agent_name, scratch_data):
    """
    Create complete agent directory structure in both Synthetic_Base and Synthetic populations.

    Args:
        agent_name (str): The agent's identifier
        scratch_data (dict): The agent's scratch data
    """
    populations = ["Synthetic_Base", "Synthetic"]

    for population in populations:
        agent_dir = f"agent_bank/populations/{population}/{agent_name}"
        memory_stream_dir = f"{agent_dir}/memory_stream"

        # Create directories
        os.makedirs(agent_dir, exist_ok=True)
        os.makedirs(memory_stream_dir, exist_ok=True)

        # Create scratch.json
        scratch_path = f"{agent_dir}/scratch.json"
        with open(scratch_path, 'w') as f:
            json.dump(scratch_data, f, indent=2)

        # Create meta.json
        meta_data = {
            "population": "Synthetic",
            "id": agent_name,
            "forked_population": "Synthetic_Base",
            "forked_id": agent_name
        }
        meta_path = f"{agent_dir}/meta.json"
        with open(meta_path, 'w') as f:
            json.dump(meta_data, f, indent=2)

        # Create memory_stream/nodes.json (empty list)
        nodes_path = f"{memory_stream_dir}/nodes.json"
        with open(nodes_path, 'w') as f:
            json.dump([], f)

        # Create memory_stream/embeddings.json (empty dict)
        embeddings_path = f"{memory_stream_dir}/embeddings.json"
        with open(embeddings_path, 'w') as f:
            json.dump({}, f)

        # Create inventory.json (only for Synthetic population with basic structure)
        if population == "Synthetic":
            inventory_data = {
                "items": [
                    {
                        "name": "digital cash",
                        "quantity": 1000.0,
                        "value": 1.0,
                        "production_cost": 0.0,
                        "description": "Starting business cash",
                        "created": 1,
                        "last_modified": 1
                    }
                ],
                "records": [
                    {
                        "record_id": 0,
                        "action": "add",
                        "item_name": "digital cash",
                        "quantity": 1000,
                        "time_step": 1,
                        "description": "Starting business cash",
                        "trade_partner": ""
                    }
                ],
                "production_plans": []
            }
            inventory_path = f"{agent_dir}/inventory.json"
            with open(inventory_path, 'w') as f:
                json.dump(inventory_data, f, indent=2)


def load_agent_memories(agent_name):
    """
    Load memories for an agent from the generated memory file.

    Args:
        agent_name (str): The agent's identifier

    Returns:
        list: Combined list of all memories
    """
    memory_file = f"testing/memories/{agent_name}_memories.py"
    if not os.path.exists(memory_file):
        raise FileNotFoundError(f"Memory file not found: {memory_file}")

    # Load the Python file as a module
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_memories", memory_file)
    agent_memories_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_memories_module)

    # Return the combined memories
    memory_var_name = f"{agent_name}_memories"
    if hasattr(agent_memories_module, memory_var_name):
        return getattr(agent_memories_module, memory_var_name)
    else:
        raise AttributeError(f"No variable named '{memory_var_name}' found in memory file")


# Example usage
if __name__ == "__main__":
    # Example: Generate memories for Bianca Silva
    generate_agent_memories_from_text(agent_name="test_agent",
    population_name="Synthetic_Base",
    text_file_name="test_memories.txt"
)

    # Example: Load generated memories
    # memories = load_agent_memories("bianca_silva")
    # print(f"Loaded {len(memories)} memories for the agent")
    pass


def remember_memories_to_agent(agent_name, memories):
    """
    Add memories to an agent using the same pattern as build_agent in main.py

    Args:
        agent_name (str): The agent's identifier (e.g., "kemi_adebayo")
        memories (list): List of memory strings to add
    """
    from generative_agent.generative_agent import GenerativeAgent
    from main import setup_agent_inventory

    # Load agent from Synthetic_Base
    agent = GenerativeAgent("Synthetic_Base", agent_name)

    # Add each memory
    for m in memories:
        agent.remember(m)

    # Setup inventory
    setup_agent_inventory(agent, agent_name)

    # Save to Synthetic population
    agent.save("Synthetic", agent_name)