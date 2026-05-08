"""
agents/caldera_agents.py
─────────────────────────
An LLM-powered agent that plans and orchestrates MITRE Caldera operations.

The agent is given a high-level red-team objective and autonomously:
  1. Lists available Caldera abilities
  2. Selects relevant abilities for the objective
  3. Creates an adversary profile
  4. Starts an operation and monitors it
  5. Collects and summarises results
"""

import time
from groq import Groq
from actions.agent_actions import parse_action, dispatch_action, list_available_actions
from utils.shared_config import config
from utils.logs import get_logger
from utils.constants import AGENT_LOOP_DELAY

logger = get_logger(__name__)


class CalderaAgent:
    """
    Autonomously runs MITRE Caldera red-team operations guided by an LLM.
    """

    SYSTEM_PROMPT = """\
You are a red-team operator specialised in MITRE Caldera.
Your job is to plan and execute adversary emulation operations.

## Workflow
1. Use caldera_list_abilities to see what techniques are available.
2. Pick abilities that match the objective (use MITRE ATT&CK IDs where possible).
3. Create an adversary with caldera_create_adversary.
4. Start an operation with caldera_start_operation.
5. Poll caldera_get_operation until state is "finished".
6. Retrieve results with caldera_get_results and summarise them.

## How to call a tool
```json
{{"action": "<action_name>", "parameters": {{"arg1": "val1"}}}}
```

Available tools:
{tools}

When done, write "DONE: <summary>".
"""

    def __init__(self, model: str = config.LLM_MODEL, max_iterations: int = config.MAX_ITERATIONS):
        self.model = model
        self.max_iterations = max_iterations
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.history: list[dict] = []

    def _build_system(self) -> str:
        return self.SYSTEM_PROMPT.format(tools=list_available_actions())

    def _call_llm(self) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=self._build_system(),
            messages=self.history,
        )
        return response.content[0].text

    def run(self, objective: str) -> str:
        """
        Execute a Caldera-based red-team engagement.

        Args:
            objective: e.g. 'Perform credential dumping on Windows hosts in the red group'

        Returns:
            Final summary of what was executed and the results
        """
        logger.info(f"[CalderaAgent] Objective: {objective}")
        self.history = [{"role": "user", "content": objective}]

        final_output = ""
        for i in range(1, self.max_iterations + 1):
            logger.info(f"[CalderaAgent] Iteration {i}")
            llm_output = self._call_llm()
            self.history.append({"role": "assistant", "content": llm_output})

            if "DONE:" in llm_output:
                final_output = llm_output
                break

            action = parse_action(llm_output)
            if action is None:
                final_output = llm_output
                break

            try:
                result = dispatch_action(action)
                result_str = str(result)
            except Exception as exc:
                result_str = f"ERROR: {exc}"
                logger.error(f"[CalderaAgent] {exc}")

            self.history.append({
                "role": "user",
                "content": f"Result of {action.name}:\n{result_str}",
            })
            time.sleep(AGENT_LOOP_DELAY)
        else:
            final_output = "Max iterations reached."

        return final_output
