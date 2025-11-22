"""
Configuration settings for the Multi-Agent Research Assistant.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LLM Settings
LLM_MODEL = "llama-3.1-8b-instant"  # Fast and free on Groq
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 4096

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
LOG_LEVEL = "DEBUG"
