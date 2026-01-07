import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# In a real app, these would come from environment variables
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "local-model")
VISION_MODEL = os.getenv("VISION_MODEL", "local-model")

client = OpenAI(base_url=LM_STUDIO_URL, api_key=API_KEY)


def get_client():
    return client


def get_model(vision=False):
    return VISION_MODEL if vision else DEFAULT_MODEL


import re


def extract_code_block(llm_response):
    if not llm_response:
        return ""
    # Standard markdown code block regex
    pattern = r"```(?:typescript|ts|javascript|js)?\n(.*?)```"
    match = re.search(pattern, llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: Clean up prefix text or single line backticks
    llm_response = llm_response.replace("```typescript", "").replace("```ts", "").replace("```", "").strip()

    lines = llm_response.split('\n')
    clean_lines = [l for l in lines if not l.lower().strip().startswith(("here", "sure", "certainly", "i have"))]
    return '\n'.join(clean_lines).strip()
