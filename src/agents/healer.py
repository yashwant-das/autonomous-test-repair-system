import os
import subprocess
import sys

from src.utils.llm import get_client, get_model, extract_code_block
from src.utils.validation import validate_file_path

# Add the project root to sys.path to support 'src.' imports when run as a script
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..")))


def run_test(test_file):
    """
    Run a Playwright test file.

    Args:
        test_file: Path to the test file

    Returns:
        subprocess.CompletedProcess result
    """
    print(f"Running {test_file}...")
    try:
        result = subprocess.run(
            ["npx", "playwright", "test", test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(
                os.path.dirname(__file__)))  # Project root
        )
        return result
    except subprocess.TimeoutExpired:
        # Create a mock result for timeout
        class TimeoutResult:
            returncode = 1
            stdout = ""
            stderr = "Test execution timed out after 60 seconds"

        return TimeoutResult()
    except FileNotFoundError:
        class NotFoundResult:
            returncode = 1
            stdout = ""
            stderr = "Playwright not found. Please run 'npx playwright install'"

        return NotFoundResult()


def heal_code(file_path, error_log, current_code):
    """
    Use LLM to heal broken test code.

    Args:
        file_path: Path to the test file
        error_log: Error log from test execution
        current_code: Current (broken) test code

    Returns:
        Fixed code string, or original code if healing fails
    """
    if not current_code or not current_code.strip():
        return current_code

    system_prompt = """
    You are a Playwright Self-Healing Agent.
    I will provide you with a BROKEN Playwright test and the Error Log.
    
    YOUR JOB:
    1. Analyze the error (e.g., "Locator not found").
    2. Fix the specific line in the code (Update selectors).
    3. Return ONLY the fixed full code block wrapped in markdown ```ts ... ```.
    """

    user_prompt = f"""
    FILE: {file_path}
    BROKEN CODE:
    ```typescript
    {current_code}
    ```
    ERROR LOG:
    {error_log}
    """

    client = get_client()
    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )

        if not response.choices or not response.choices[0].message.content:
            print("LLM returned empty response")
            return current_code

        raw_response = response.choices[0].message.content
        fixed_code = extract_code_block(raw_response)

        if not fixed_code or fixed_code == current_code:
            print("LLM did not produce valid fixed code")
            return current_code

        return fixed_code
    except Exception as e:
        print(f"LLM Error: {e}")
        return current_code


def attempt_healing(test_file, max_retries=1):
    """
    Attempt to heal a broken test file.

    Args:
        test_file: Path to the test file to heal
        max_retries: Maximum number of healing attempts (default: 1)

    Returns:
        Result message string
    """
    try:
        # Validate file path
        validated_path = validate_file_path(test_file)
    except Exception as e:
        return f"Validation Error: {str(e)}"

    if not os.path.exists(validated_path):
        return f"Error: File not found at {validated_path}"

    # Initial test run
    result = run_test(validated_path)
    if result.returncode == 0:
        return "Test passed (No healing needed)."

    # Read the broken code
    try:
        with open(validated_path, "r", encoding="utf-8") as f:
            broken_code = f.read()
    except IOError as e:
        return f"Error reading test file: {str(e)}"

    if not broken_code.strip():
        return "Error: Test file is empty"

    # Attempt healing
    for attempt in range(max_retries + 1):
        # Combine stdout and stderr for the LLM to have full context
        combined_logs = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        fixed_code = heal_code(validated_path, combined_logs, broken_code)

        if not fixed_code or fixed_code == broken_code:
            return f"Healing attempt {attempt + 1} did not produce changes. Original error:\n{combined_logs[:500]}"

        # Write the fixed code
        try:
            with open(validated_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
        except IOError as e:
            return f"Error writing fixed code: {str(e)}"

        # Test the fixed code
        final_result = run_test(validated_path)
        if final_result.returncode == 0:
            return f"SUCCESS: The Agent self-healed the test!\nFixed code applied to {validated_path}"

        # If healing failed, update broken_code for next attempt
        broken_code = fixed_code
        result = final_result

    # All attempts failed
    err_logs = final_result.stdout if final_result.stdout else final_result.stderr
    return f"Healing failed after {max_retries + 1} attempt(s). Latest error:\n{err_logs[:500]}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.agents.healer <path_to_test_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    print(f"Attempting to heal: {test_file}")
    result = attempt_healing(test_file)
    print(result)
