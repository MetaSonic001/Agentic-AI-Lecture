"""
Configuration settings for the Multi-Agent Research Assistant using Phidata/Agno.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LLM Settings (for Phidata agents)
LLM_MODEL = "llama-3.1-70b-versatile"  # Groq's best model
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 8192

# Research Settings
MAX_SOURCES = 3
MAX_SEARCH_RESULTS = 5
REQUEST_TIMEOUT = 10

# Review Settings
MAX_REVIEW_ITERATIONS = 2

# Output Settings
OUTPUT_DIR = "outputs"
CHARTS_DIR = "outputs/charts"

# Logging
LOG_FILE = "logs/research_assistant.log"
LOG_LEVEL = "INFO"