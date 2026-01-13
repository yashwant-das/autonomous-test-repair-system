"""
LLM client utilities for OpenAI-compatible API interactions.

This module provides functions for initializing the LLM client, selecting models,
and extracting code blocks from LLM responses.
"""

import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configuration from environment variables
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "local-model")
VISION_MODEL = os.getenv("VISION_MODEL", "local-model")

client = OpenAI(base_url=LM_STUDIO_URL, api_key=API_KEY)


def get_client():
    """Get the configured OpenAI-compatible client instance.

    Returns:
        OpenAI: Configured client instance
    """
    return client


def get_model(vision=False):
    """Get the appropriate model name based on use case.

    Args:
        vision: If True, returns vision model; otherwise returns default model

    Returns:
        str: Model name string
    """
    return VISION_MODEL if vision else DEFAULT_MODEL


def extract_code_block(llm_response):
    """Extract code block from LLM response text.

    Attempts to extract code from markdown code blocks, with fallback
    to cleaning up response text if no code block is found.

    Args:
        llm_response: Raw LLM response text

    Returns:
        str: Extracted code block, or cleaned response if no block found
    """
    if not llm_response:
        return ""
    # Standard markdown code block regex
    pattern = r"```(?:typescript|ts|javascript|js)?\n(.*?)```"
    match = re.search(pattern, llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: Clean up prefix text or single line backticks
    llm_response = (
        llm_response.replace("```typescript", "")
        .replace("```ts", "")
        .replace("```", "")
        .strip()
    )

    lines = llm_response.split("\n")
    clean_lines = [
        line
        for line in lines
        if not line.lower().strip().startswith(("here", "sure", "certainly", "i have"))
    ]
    return "\n".join(clean_lines).strip()


def extract_json_block(llm_response):
    """Extract JSON block from LLM response text.

    Args:
        llm_response: Raw LLM response text

    Returns:
        str: Extracted JSON string
    """
    if not llm_response:
        return "{}"

    # Check for markdown code block
    pattern = r"```(?:json)?\n(.*?)```"
    match = re.search(pattern, llm_response, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # Fallback: look for first { and last }
        start = llm_response.find("{")
        end = llm_response.rfind("}")

        if start != -1 and end != -1:
            json_str = llm_response[start : end + 1]
        else:
            json_str = llm_response

    # Sanitization: Remove invalid control characters (0x00-0x1F) except \n, \r, \t
    # Also remove 0x7F (DEL)
    json_str = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", json_str)

    return json_str
