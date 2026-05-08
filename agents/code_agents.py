"""
agents/code_agents.py
──────────────────────
An agentic loop that can write and execute code / shell commands
to accomplish a given security task.
"""

import time
from groq import Groq
from actions.agent_actions import parse_action, dispatch_action, list_available_actions
from utils.shared_config import config
from utils.logs import get_logger
from utils.constants import AGENT_LOOP_DELAY

logger = get_logger(__name__)


class CodeAgent:
    """
    ReAct-style agent that iteratively:
      1. Asks the LLM what to do next
      2. Parses a structured action from the LLM output
      3. Executes the action (shell / Python / file ops)
      4. Feeds the result back to the LLM
      5. Repeats until the LLM says it is DONE
    """

    SYSTEM_PROMPT = """\
You are an expert penetration tester and red-team operator.
You help security researchers by writing and executing code.

## How to call a tool
When you want to run a tool emit a JSON action block like this:

```json
{{"action": "<action_name>", "parameters": {{"arg1": "val1"}}}}
```

Available tools:
{tools}

## Rules
- Always explain your reasoning BEFORE the JSON block.
- After receiving a tool result, analyse it and decide the next step.
- When the task is complete, write "DONE: <summary>" with NO json block.
- Never reveal credentials or sensitive info in your output.
"""

    def __init__(self, model: str = config.LLM_MODEL, max_iterations: int = config.MAX_ITERATIONS):
        self.model = model
        self.max_iterations = max_iterations
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.history: list[dict] = []

    def _build_system(self) -> str:
        return self.SYSTEM_PROMPT.format(tools=list_available_actions())

    def _call_llm(self) -> str:
       response = self.client.chat.completions.create(
           model=self.model,
           max_tokens=config.MAX_TOKENS,
           messages=[{"role": "system", "content": self._build_system()}, *self.history],
           )
       return response.choices[0].message.content

    def run(self, task: str) -> str:
        """
        Run the agent loop for the given task.

        Args:
            task: natural language description of what to accomplish

        Returns:
            The agent's final summary string
        """
        logger.info(f"[CodeAgent] Starting task: {task}")
        self.history = [{"role": "user", "content": task}]

        final_output = ""
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"[CodeAgent] Iteration {iteration}/{self.max_iterations}")

            llm_output = self._call_llm()
            logger.debug(f"[CodeAgent] LLM: {llm_output[:300]}")
            self.history.append({"role": "assistant", "content": llm_output})

            # Check for completion
            if "DONE:" in llm_output:
                final_output = llm_output
                logger.info("[CodeAgent] Task completed")
                break

            # Try to dispatch an action
            action = parse_action(llm_output)
            if action is None:
                logger.info("[CodeAgent] No action found — treating as final answer")
                final_output = llm_output
                break

            try:
                result = dispatch_action(action)
                result_str = str(result)
            except Exception as exc:
                result_str = f"ERROR: {exc}"
                logger.error(f"[CodeAgent] Action error: {exc}")

            # Feed result back
            self.history.append({
                "role": "user",
                "content": f"Tool result for '{action.name}':\n{result_str}",
            })
            time.sleep(AGENT_LOOP_DELAY)
        else:
            logger.warning("[CodeAgent] Max iterations reached")
            final_output = "Max iterations reached without completing the task."

        return final_output
