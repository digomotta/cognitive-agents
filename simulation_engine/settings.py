import sys
import os
from pathlib import Path

# Read API key from environment. Do not hardcode secrets in source control.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
KEY_OWNER = "Rodrigo da Motta"
DEBUG = False #False
MAX_CHUNK_SIZE = 4
LLM_VERS = "gpt-5-mini"
LLM_ANALYZE_VERS = "gpt-5"
MAX_TOKENS_CONV = 500
BASE_DIR = f"{Path(__file__).resolve().parent.parent}"
POPULATIONS_DIR = f"{BASE_DIR}/agent_bank/populations"
LLM_PROMPT_DIR = f"{BASE_DIR}/simulation_engine/prompt_template"