"""
Utility for loading LLM prompts from external markdown files.
"""

from pathlib import Path


def load_prompt(agent_name: str) -> str:
    """Load a prompt from the prompts/ directory.

    Args:
        agent_name: Name of the agent (e.g., 'generator', 'healer', 'vision')

    Returns:
        str: Content of the prompt file
    """
    # Resolve the project root dynamically
    project_root = Path(__file__).resolve().parent.parent.parent
    prompt_path = project_root / "prompts" / f"{agent_name}.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()
