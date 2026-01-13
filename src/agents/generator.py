"""
Test generation agent for creating Playwright test scripts.

This module generates TypeScript Playwright tests from URLs and feature descriptions
using LLM-based code generation.
"""

import os
import subprocess
import sys

from src.utils.browser import extract_domain, fetch_page_context
from src.utils.llm import extract_code_block, get_client, get_model

# Add the project root to sys.path to support 'src.' imports when run as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

TEST_DIR = "tests/generated"
os.makedirs(TEST_DIR, exist_ok=True)


def generate_test_script(url, feature_description):
    """Generate a Playwright test script from a URL and feature description.

    Args:
        url: Validated URL string
        feature_description: Validated feature description string

    Returns:
        str: Generated TypeScript test code, or error message if generation fails
    """
    try:
        html_context = fetch_page_context(url)

        if "Error" in html_context:
            return html_context

        system_instruction = """
    You are a Senior QA Automation Engineer.
    Write a complete, runnable Playwright (TypeScript) test file.

    RULES:
    1. Use 'import { test, expect } from "@playwright/test";'
    2. Analyze the HTML to find 'data-test', 'id', or specific 'class' selectors.
    3. Output ONLY the code block. No markdown backticks (```).
    """

        user_prompt = f"""
    TARGET URL: {url}
    USER STORY: {feature_description}
    PAGE CONTEXT: {html_context}
    """

        client = get_client()
        try:
            response = client.chat.completions.create(
                model=get_model(),
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )

            if not response.choices or not response.choices[0].message.content:
                return "Error: LLM returned empty response"

            code = extract_code_block(response.choices[0].message.content)
            if not code:
                return "Error: Could not extract code block from LLM response"

            return code

        except Exception as e:
            return f"LLM Error: {str(e)}"

    except Exception as e:
        return f"Error generating test script: {str(e)}"


def run_generated_test(url, code_snippet, description="test"):
    """Run a generated test script using Playwright.

    Args:
        url: Validated URL string
        code_snippet: TypeScript test code to run
        description: Test description for filename generation

    Returns:
        str: Test execution result message (pass/fail with logs)
    """
    if not code_snippet or not code_snippet.strip():
        return "Error: No test code provided"

    try:
        # Using the new naming convention: [domain]_[description]_[YYYYMMDD_HHMMSS].spec.ts
        import re
        from datetime import datetime

        domain = extract_domain(url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Meaningful snake_case sanitization (limited to alphanumeric and simple hyphens)
        clean_desc = re.sub(r"[^a-zA-Z0-9]", "_", description).lower()
        # Remove consecutive underscores
        clean_desc = re.sub(r"_+", "_", clean_desc)
        snake_desc = clean_desc[:40].strip("_")

        filename = f"{domain}_{snake_desc}_{timestamp}.spec.ts"
        filepath = os.path.join(TEST_DIR, filename)

        # Validate filepath before writing
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_snippet)

        print(f"Running {filename}...")

        # Subprocess run uses a list, so shell quoting is handled automatically.

        try:
            result = subprocess.run(
                ["npx", "playwright", "test", filepath],
                capture_output=True,
                text=True,
                timeout=45,
                cwd=os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))
                ),  # Project root
            )

            if result.returncode == 0:
                return f"TEST PASSED!\nStored in: {filepath}\n\nLogs:\n{result.stdout}"
            else:
                # Check if stdout has more useful info than stderr in case of playwright failures
                logs = result.stdout if result.stdout else result.stderr
                return f"TEST FAILED.\nStored in: {filepath}\n\nLogs:\n{logs}"

        except subprocess.TimeoutExpired:
            return f"Error: Test execution timed out after 45 seconds.\nStored in: {filepath}"
        except FileNotFoundError:
            return "Error: Playwright not found. Please run 'npx playwright install'"
        except Exception as e:
            return f"Execution Error: {str(e)}\nStored in: {filepath}"

    except Exception as e:
        return f"Error running test: {str(e)}"
