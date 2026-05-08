import logging
from groq import Groq
import os

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self, model="llama-3.1-8b-instant"):
        self.model = model
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.system_prompt = """You are a cybersecurity research analyst. 
        When given a research topic, you provide:
        1. A detailed overview of the topic
        2. Latest trends and developments
        3. Key statistics and facts
        4. Real-world examples
        5. Recommendations and mitigations
        Always be thorough, accurate, and structured in your responses."""

    def run(self, task: str) -> str:
        logger.info(f"[ResearchAgent] Researching: {task[:50]}…")
        
        message = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task}
            ],
            max_tokens=2048,
        )
        
        result = message.choices[0].message.content
        logger.info(f"[ResearchAgent] Research complete ({len(result)} chars)")
        return result