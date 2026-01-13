"""
Vision-based test generation agent using screenshot analysis.

This module captures UI screenshots and uses vision-capable LLMs to generate
Playwright test scripts based on visual analysis.
"""

import base64
import os
import sys
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from src.utils.browser import extract_domain
from src.utils.llm import extract_code_block, get_client, get_model

# Add the project root to sys.path to support 'src.' imports when run as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

SCREENSHOT_DIR = "tests/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def encode_image(image_path):
    """Encode an image file to base64 for LLM vision API.

    Args:
        image_path: Path to the image file

    Returns:
        str: Base64 encoded string

    Raises:
        FileNotFoundError: If image file doesn't exist
        IOError: If file cannot be read
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Screenshot not found: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except IOError as e:
        raise IOError(f"Error reading screenshot: {str(e)}")


def analyze_visual_ui(url, instruction):
    """Analyze a UI using vision-capable LLM and generate a test script.

    Captures a screenshot of the target URL and uses vision LLM to analyze
    the UI and generate appropriate Playwright test code.

    Args:
        url: Validated URL string
        instruction: Validated instruction string describing the action to perform

    Returns:
        str: Generated TypeScript test code, or error message if generation fails
    """
    import re

    try:
        domain = extract_domain(url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Meaningful snake_case sanitization
        clean_inst = re.sub(r"[^a-zA-Z0-9\s]", "", instruction).lower()
        snake_inst = "_".join(clean_inst.split())[:30]

        screenshot_name = f"{domain}_{snake_inst}_{timestamp}.png"
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)

        # Ensure screenshot directory exists
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(2)  # Wait for animations
                page.screenshot(path=screenshot_path)
                browser.close()
        except Exception as e:
            return f"Error capturing screenshot: {str(e)}"

        if not os.path.exists(screenshot_path):
            return f"Error: Screenshot was not created at {screenshot_path}"

        try:
            base64_image = encode_image(screenshot_path)
        except (FileNotFoundError, IOError) as e:
            return f"Error encoding image: {str(e)}"

        system_instruction = """
    You are a Test Automation Expert.
    Analyze the UI screenshot provided.
    Write a complete Playwright test (TypeScript) that performs the user's requested action.

    RULES:
    1. Always begin the test by navigating to the TARGET URL provided.
    2. Use 'import { test, expect } from "@playwright/test";'
    3. SELECTOR STRATEGY:
       - If text appears INSIDE an input field, it is likely a placeholder. Use `page.getByPlaceholder('...')`.
       - For buttons, use `page.getByRole('button', { name: '...' })`.
       - If text is a label next to or above a field, use `page.getByLabel('...')`.
       - Prefer user-visible text (getByText) for general assertions.
    4. Focus on robust, user-visible locators.
    """

        client = get_client()
        try:
            response = client.chat.completions.create(
                model=get_model(vision=True),
                messages=[
                    {"role": "system", "content": system_instruction},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"TARGET URL: {url}\nUser Scenario: {instruction}",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            if not response.choices or not response.choices[0].message.content:
                return "Error: Vision LLM returned empty response"

            code = extract_code_block(response.choices[0].message.content)
            if not code:
                return "Error: Could not extract code block from vision LLM response"

            return code
        except Exception as e:
            return f"Vision LLM Error: {str(e)}"

    except Exception as e:
        return f"Error analyzing visual UI: {str(e)}"
