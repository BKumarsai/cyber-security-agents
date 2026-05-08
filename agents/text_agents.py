"""
agents/text_agents.py
──────────────────────
A simple question-answer agent: no tool use, just a single LLM call.
Great for summarisation, report writing, or explaining findings.
"""

from groq import Groq
from utils.shared_config import config
from utils.logs import get_logger

logger = get_logger(__name__)


class TextAgent:
    """
    Calls the LLM once and returns a plain-text response.
    Use this for:
      - Summarising scan results
      - Writing penetration test reports
      - Explaining CVEs / techniques
      - Any task that doesn't need tool calls
    """

    SYSTEM_PROMPT = (
        "You are an expert cybersecurity analyst with deep knowledge of offensive "
        "and defensive security techniques, the MITRE ATT&CK framework, penetration "
        "testing methodologies, and vulnerability assessment.  Be thorough, accurate, "
        "and structure your answers clearly."
    )

    def __init__(self, model: str = config.LLM_MODEL):
        self.model = model
        self.client = Groq(api_key=config.GROQ_API_KEY)

    def run(self, prompt: str, system: str | None = None) -> str:
        """
        Send a prompt to the LLM and return the text response.

        Args:
            prompt: user message
            system: optional system prompt override

        Returns:
            LLM response as a plain string
        """
        logger.info(f"[TextAgent] Calling LLM: {prompt[:100]}…")
        message = self.client.chat.completions.create(
              model=self.model,
              max_tokens=config.MAX_TOKENS,
              messages=[
                    {"role": "system", "content": system or self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    ],
        )
        response = message.choices[0].message.content
        logger.info(f"[TextAgent] Response received ({len(response)} chars)")
        return response

    def summarise_results(self, raw_results: str) -> str:
        """Summarise raw tool / scan results in plain English."""
        prompt = (
            f"Please analyse and summarise the following cybersecurity scan results.  "
            f"Identify key findings, vulnerabilities, and recommended actions:\n\n"
            f"{raw_results}"
        )
        return self.run(prompt)

    def explain_technique(self, technique_id: str) -> str:
        """Explain a MITRE ATT&CK technique."""
        prompt = (
            f"Explain MITRE ATT&CK technique {technique_id}: what it is, how attackers "
            f"use it, detection strategies, and mitigations."
        )
        return self.run(prompt)
