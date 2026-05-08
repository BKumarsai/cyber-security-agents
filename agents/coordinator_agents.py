"""
agents/coordinator_agents.py
"""


from groq import Groq
from utils.shared_config import config
from utils.logs import get_logger
from agents.caldera_agents import CalderaAgent
from agents.code_agents import CodeAgent
from agents.text_agents import TextAgent

logger = get_logger(__name__)

COORDINATOR_SYSTEM = """\
You are a senior red-team coordinator managing a team of AI security agents.
Your available agents:

  - CALDERA_AGENT  → use for MITRE Caldera / adversary emulation tasks
  - CODE_AGENT     → use for shell commands, scripts, file operations
  - TEXT_AGENT     → use for analysis, summarisation, report writing

Given a high-level security objective, produce a numbered task list.
For each task, state which agent should handle it and what exactly to ask.

Output format (strict):
PLAN:
1. [AGENT_TYPE] Task description
2. [AGENT_TYPE] Task description
...
END_PLAN

After producing the plan, execute each step by delegating to the right agent.
When all steps are done write:
FINAL_REPORT:
<detailed markdown report of all findings>
"""


class CoordinatorAgent:

    def __init__(self, model: str = config.LLM_MODEL):
        self.model = model
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.caldera_agent = CalderaAgent(model=model)
        self.code_agent    = CodeAgent(model=model)
        self.text_agent    = TextAgent(model=model)

    def _call_llm(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            messages=messages,
        )
        return response.choices[0].message.content

    def _parse_plan(self, plan_text: str) -> list[tuple[str, str]]:
        import re
        steps: list[tuple[str, str]] = []
        pattern = re.compile(r"\d+\.\s*\[?(CALDERA_AGENT|CODE_AGENT|TEXT_AGENT)\]?\s*(.+)")
        for line in plan_text.split("\n"):
            m = pattern.match(line.strip())
            if m:
                steps.append((m.group(1), m.group(2).strip()))
        return steps

    def _delegate(self, agent_type: str, task: str) -> str:
        logger.info(f"[Coordinator] → {agent_type}: {task[:100]}")
        if agent_type == "CALDERA_AGENT":
            return self.caldera_agent.run(task)
        elif agent_type == "CODE_AGENT":
            return self.code_agent.run(task)
        elif agent_type == "TEXT_AGENT":
            return self.text_agent.run(task)
        else:
            return f"Unknown agent type: {agent_type}"

    def run(self, objective: str) -> str:
        logger.info(f"[Coordinator] Objective: {objective}")

        # Step 1 — build initial messages with system prompt
        messages = [
            {"role": "system", "content": COORDINATOR_SYSTEM},
            {"role": "user",   "content": objective},
        ]

        # Step 2 — get the plan
        plan_text = self._call_llm(messages)
        logger.info(f"[Coordinator] Plan:\n{plan_text}")
        messages.append({"role": "assistant", "content": plan_text})

        # Step 3 — parse and execute each step
        steps = self._parse_plan(plan_text)
        if not steps:
            logger.warning("[Coordinator] No parseable steps — delegating to CodeAgent")
            return self.code_agent.run(objective)

        results: list[str] = []
        for i, (agent_type, task) in enumerate(steps, 1):
            logger.info(f"[Coordinator] Executing step {i}/{len(steps)}")
            result = self._delegate(agent_type, task)
            results.append(f"### Step {i} ({agent_type}): {task}\n\n{result}")
            messages.append({
                "role": "user",
                "content": f"Step {i} result:\n{result}",
            })

        # Step 4 — ask for final report
        messages.append({
            "role": "user",
            "content": "All steps complete. Write the FINAL_REPORT now.",
        })
        final_report = self._call_llm(messages)
        logger.info("[Coordinator] Final report generated")
        return final_report