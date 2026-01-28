"""
Formatting utilities for the application.
"""

import re


def clean_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text.

    Args:
        text: Input string containing potential ANSI codes

    Returns:
        str: Cleaned string
    """
    if not text:
        return ""
    # Regex to match ANSI escape codes
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def format_test_result(filepath: str, output: str, success: bool) -> str:
    """Format the test execution result for display.

    Args:
        filepath: Path to the test file
        output: Raw output from the test execution
        success: Whether the test passed or failed

    Returns:
        str: Formatted user-friendly message
    """
    cleaned_output = clean_ansi_codes(output)
    
    # Remove some common noisy lines if present
    cleaned_output = cleaned_output.replace("To open last HTML report run:", "")
    cleaned_output = cleaned_output.replace("npx playwright show-report", "")
    
    # Trim excessive whitespace
    cleaned_output = cleaned_output.strip()

    status = "PASSED" if success else "FAILED"
    icon = "✅" if success else "❌"
    
    return f"""{icon} TEST {status}
Stored in: {filepath}

Logs:
{cleaned_output}
"""
