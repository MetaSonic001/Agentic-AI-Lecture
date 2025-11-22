"""
LLM Client using Groq for fast inference.
"""
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, MAX_TOKENS
from logger_setup import log


class LLMClient:
    """Wrapper for Groq LLM API calls."""
    
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = LLM_MODEL
        log.info(f"LLM Client initialized with model: {self.model}")
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = None) -> str:
        """Generate a response from the LLM."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            log.debug(f"Sending prompt to LLM (length: {len(prompt)} chars)")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or LLM_TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            result = response.choices[0].message.content
            log.debug(f"Received response (length: {len(result)} chars)")
            
            return result
            
        except Exception as e:
            log.error(f"LLM generation failed: {str(e)}")
            raise


# Singleton instance
llm_client = None

def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client
