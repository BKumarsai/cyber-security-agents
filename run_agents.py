"""
run_agents.py
─────────────
Main entry point.  Run this to start an agent from the command line.

Usage:
    python run_agents.py --agent text   --task "Explain CVE-2021-44228"
    python run_agents.py --agent code   --task "List files in /tmp and check for SUID binaries"
    python run_agents.py --agent caldera --task "Run a discovery operation on the red group"
    python run_agents.py --agent coord  --task "Full engagement: recon web server then report"
    python run_agents.py --agent research --task "What are the latest cybersecurity threats in 2026"
"""

import argparse
import sys
from utils.shared_config import config
from utils.logs import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cybersecurity LLM Agents — CLI Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent",
        choices=["text", "code", "caldera", "coord","research"],
        required=True,
        help="Which agent to run",
    )
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Task / objective for the agent (use quotes for multi-word tasks)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=config.LLM_MODEL,
        help=f"LLM model to use (default: {config.LLM_MODEL})",
    )
    args = parser.parse_args()

    # Validate API keys
    if not config.validate():
        sys.exit(1)

    logger.info(f"Starting agent='{args.agent}' model='{args.model}'")
    logger.info(f"Task: {args.task}")
    print("─" * 60)

    result: str

    if args.agent == "text":
        from agents.text_agents import TextAgent
        agent = TextAgent(model=args.model)
        result = agent.run(args.task)

    elif args.agent == "code":
        from agents.code_agents import CodeAgent
        agent = CodeAgent(model=args.model)
        result = agent.run(args.task)

    elif args.agent == "caldera":
        from agents.caldera_agents import CalderaAgent
        agent = CalderaAgent(model=args.model)
        result = agent.run(args.task)

    elif args.agent == "coord":
        from agents.coordinator_agents import CoordinatorAgent
        agent = CoordinatorAgent(model=args.model)
        result = agent.run(args.task)

    elif args.agent == "research":
        from agents.research_agents import ResearchAgent
        agent = ResearchAgent(model=args.model)
        result = agent.run(args.task)

    else:
        print(f"Unknown agent: {args.agent}")
        sys.exit(1)

    print("\n" + "═" * 60)
    print("RESULT:")
    print("═" * 60)
    print(result)
    print("═" * 60)


if __name__ == "__main__":
    main()
