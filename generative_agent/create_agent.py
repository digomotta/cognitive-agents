#!/usr/bin/env python3
"""
Agent Creation Tool

This tool creates complete generative agents with memories, inventory, and all necessary files.

Usage:
    python -m generative_agent.create_agent --name agent_name --population population_name --text text_file_name

Examples:
    python -m generative_agent.create_agent --name bianca_silva --population Synthetic_Base --text memories.txt
    python -m generative_agent.create_agent --name new_agent --population Synthetic_Base --text agent_background.txt
"""

import argparse
import json
import os
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from simulation_engine.gpt_structure import chat_safe_generate
from simulation_engine.settings import LLM_VERS
from generative_agent.generative_agent import GenerativeAgent


def generate_agent_memories_from_scratch(agent_name, population_name, output_file_path=None):
    """
    Generate comprehensive agent memories using only scratch data.

    Args:
        agent_name (str): The agent's identifier (e.g., "bianca_silva")
        population_name (str): The population name (e.g., "Synthetic_Base")
        output_file_path (str): Optional path for output file. If None, saves to testing/memories/{agent_name}_memories.py

    Returns:
        str: Path to the generated memory file
    """

    # Load agent's scratch data
    scratch_path = f"agent_bank/populations/{population_name}/{agent_name}/scratch.json"
    if not os.path.exists(scratch_path):
        raise FileNotFoundError(f"Scratch file not found: {scratch_path}")

    with open(scratch_path, 'r') as f:
        scratch_data = json.load(f)

    # Prepare inputs for the template (without text input)
    prompt_inputs = [
        f"{scratch_data['first_name']} {scratch_data['last_name']}",  # 0
        str(scratch_data['age']),  # 1
        scratch_data['sex'],  # 2
        scratch_data['address'],  # 3
        scratch_data['census_division'],  # 4
        scratch_data['education'],  # 5
        scratch_data['race'],  # 6
        scratch_data['ethnicity'],  # 7
        scratch_data['political_ideology'],  # 8
        scratch_data['political_party'],  # 9
        str(scratch_data['extraversion']),  # 10
        str(scratch_data['agreeableness']),  # 11
        str(scratch_data['conscientiousness']),  # 12
        str(scratch_data['neuroticism']),  # 13
        str(scratch_data['openness']),  # 14
        scratch_data['fact_sheet'],  # 15
        scratch_data['speech_pattern'],  # 16
        scratch_data['self_description'],  # 17
        scratch_data['private_self_description'],  # 18
        str(scratch_data.get('total_sales_failures', 0)),  # 19
        str(scratch_data.get('last_sales_failure_time', 0)),  # 20
        agent_name.lower().replace(' ', '_')  # 21
    ]

    # Generate memories using LLM with template
    try:
        generated_content, _, _, _ = chat_safe_generate(
            prompt_inputs,
            "simulation_engine/prompt_template/generative_agent/memory_generation.txt",
            model=LLM_VERS,
            temperature=0.8,
            max_tokens=4000
        )
    except Exception as e:
        raise Exception(f"LLM generation failed: {str(e)}")

    # Set default output path if not provided
    if output_file_path is None:
        os.makedirs("agent_bank/populations/memories", exist_ok=True)
        output_file_path = f"agent_bank/populations/memories/{agent_name}_memories.py"

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
    memory_file = f"agent_bank/populations/memories/{agent_name}_memories.py"
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


def generate_agent_inventory_code(agent_name, population_name, text_file_name):
    """
    Generate agent.add_to_inventory() calls from text file description.

    Args:
        agent_name (str): The agent's identifier
        population_name (str): The population name
        text_file_name (str): Name of .txt file containing inventory/business description

    Returns:
        str: Generated Python code with agent.add_to_inventory() calls
    """
    # Load agent's scratch data
    scratch_path = f"agent_bank/populations/{population_name}/{agent_name}/scratch.json"
    text_file_path = f"agent_bank/populations/{population_name}/{agent_name}/{text_file_name}"

    if not os.path.exists(scratch_path):
        raise FileNotFoundError(f"Scratch file not found: {scratch_path}")

    if not os.path.exists(text_file_path):
        raise FileNotFoundError(f"Text file not found: {text_file_path}")

    with open(scratch_path, 'r') as f:
        scratch_data = json.load(f)

    with open(text_file_path, 'r') as f:
        inventory_description = f.read().strip()

    # Prepare inputs for the inventory template
    prompt_inputs = [
        f"{scratch_data['first_name']} {scratch_data['last_name']}",  # 0
        str(scratch_data['age']),  # 1
        scratch_data['sex'],  # 2
        scratch_data['address'],  # 3
        scratch_data['education'],  # 4
        scratch_data['fact_sheet'],  # 5
        scratch_data['self_description'],  # 6
        inventory_description  # 7
    ]

    # Generate inventory code using LLM with template
    try:
        generated_inventory_code, _, _, _ = chat_safe_generate(
            prompt_inputs,
            "simulation_engine/prompt_template/generative_agent/inventory_generation.txt",
            model=LLM_VERS,
            temperature=0.7,
            max_tokens=2000
        )

        return generated_inventory_code.strip()

    except Exception as e:
        raise Exception(f"Inventory generation failed: {str(e)}")


def setup_agent_with_generated_inventory(agent_name, inventory_code):
    """
    Add memories and inventory to an agent using generated inventory code.

    Args:
        agent_name (str): The agent's identifier (e.g., "kemi_adebayo")
        inventory_code (str): Generated Python code with agent.add_to_inventory() calls
    """
    # Load agent from Synthetic_Base
    agent = GenerativeAgent("Synthetic_Base", agent_name)

    # Load and add memories
    memories = load_agent_memories(agent_name)
    for m in memories:
        agent.remember(m)

    # Execute the generated inventory code
    # Create a safe namespace for execution
    namespace = {'agent': agent}
    try:
        exec(inventory_code, namespace)
        print(f"Successfully added inventory to {agent_name}")
    except Exception as e:
        raise Exception(f"Failed to execute inventory code: {str(e)}")

    # Save to Synthetic population
    agent.save("Synthetic", agent_name)
    print(f"Agent {agent_name} saved to Synthetic population")


def create_agent(agent_name, population_name, text_file_name):
    """
    Complete agent creation workflow: generate memories from scratch, create inventory from text, and build agent

    Args:
        agent_name (str): The agent's identifier (e.g., "bianca_silva")
        population_name (str): The population name (e.g., "Synthetic_Base")
        text_file_name (str): Name of .txt file with inventory/business description

    Returns:
        str: Path to the generated memory file
    """
    print(f"Creating agent '{agent_name}' from population '{population_name}' using text file '{text_file_name}'")

    # Step 1: Generate memories from scratch data only
    print("Generating memories from scratch data...")
    memory_file_path = generate_agent_memories_from_scratch(agent_name, population_name)

    # Step 2: Generate inventory code from text file
    print("Generating inventory from text description...")
    inventory_code = generate_agent_inventory_code(agent_name, population_name, text_file_name)

    # Step 3: Create basic agent structure
    print("Creating agent directory structure...")
    scratch_path = f"agent_bank/populations/{population_name}/{agent_name}/scratch.json"
    with open(scratch_path, 'r') as f:
        scratch_data = json.load(f)
    create_agent_structure(agent_name, scratch_data)

    # Step 4: Add memories and inventory to agent
    print("Adding memories and inventory to agent...")
    setup_agent_with_generated_inventory(agent_name, inventory_code)

    print(f"Complete agent {agent_name} created successfully!")
    print(f"Generated inventory code:")
    print(inventory_code)
    return memory_file_path


def main():
    parser = argparse.ArgumentParser(description='Create a complete generative agent with memories and inventory')

    parser.add_argument('--name', required=True, help='Agent name/identifier (e.g., bianca_silva)')
    parser.add_argument('--population', default='Synthetic_Base', help='Source population name (default: Synthetic_Base)')
    parser.add_argument('--text', required=True, help='Text file name containing inventory/business description (e.g., business.txt)')
    parser.add_argument('--output', help='Optional output path for memory file')

    args = parser.parse_args()

    try:
        # Validate inputs
        scratch_path = f"agent_bank/populations/{args.population}/{args.name}/scratch.json"
        if not os.path.exists(scratch_path):
            print(f"Error: Agent scratch file not found at {scratch_path}")
            print("Make sure the agent exists in the specified population.")
            sys.exit(1)

        text_file_path = f"agent_bank/populations/{args.population}/{args.name}/{args.text}"
        if not os.path.exists(text_file_path):
            print(f"Error: Inventory description file not found at {text_file_path}")
            print("Make sure the text file with inventory/business description exists in the agent's directory.")
            sys.exit(1)

        # Create the agent
        memory_file_path = create_agent(args.name, args.population, args.text)

        print("\n" + "="*50)
        print("AGENT CREATION COMPLETE")
        print("="*50)
        print(f"Agent: {args.name}")
        print(f"Population: {args.population}")
        print(f"Text file: {args.text}")
        print(f"Memory file: {memory_file_path}")
        print(f"Agent saved to: agent_bank/populations/Synthetic/{args.name}/")

    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()