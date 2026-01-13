"""
Self-healing agent for automatically repairing broken Playwright tests.
Refactored for Phase 1: Explainable Healing.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

from src.models.healing_model import (
    HealingDecision,
    FailureType,
    Evidence,
    HealingAction,
    ExecutionTimeline,
)
from src.utils.validation import validate_file_path
from src.utils.llm import get_client, get_model, extract_json_block

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

ARTIFACTS_DIR = "tests/artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def run_test(test_file):
    """Run a Playwright test file and return execution result."""
    print(f"Running {test_file}...")
    try:
        result = subprocess.run(
            ["npx", "playwright", "test", test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        )
        return result
    except subprocess.TimeoutExpired:

        class TimeoutResult:
            returncode = 1
            stdout = ""
            stderr = "Test execution timed out after 60 seconds"

        return TimeoutResult()
    except FileNotFoundError:

        class NotFoundResult:
            returncode = 1
            stdout = ""
            stderr = "Playwright not found"

        return NotFoundResult()


def gather_evidence(test_file, result):
    """Collect evidence from the failed test run."""
    logs = result.stderr if result.stderr else result.stdout

    # Placeholder for screenshot: usually Playwright traces/screenshots are in test-results/
    screenshot_path = None
    results_dir = "test-results"

    # Basic logic to find most recent screenshot in test-results if it exists
    if os.path.exists(results_dir):
        # This could be improved to find the specific test's screenshot
        pass

    return Evidence(error_log=logs, screenshot_path=screenshot_path, dom_snippet=None)


def classify_failure_heuristic(logs: str) -> tuple[FailureType, float, str]:
    """
    Determininstically classify failure based on regex patterns.
    Returns: (FailureType, Confidence, Reasoning)
    """

    if not logs:
        return (FailureType.UNKNOWN, 0.0, "No logs available")

    # 1. Timeout / Waiting
    if (
        "TimeoutError" in logs
        or "waiting for selector" in logs
        or "Test execution timed out" in logs
    ):
        return (
            FailureType.TIMEOUT,
            1.0,
            "Detected 'TimeoutError' or 'waiting for selector' in logs",
        )

    # 2. Target Closed / Environment
    if "TargetClosedError" in logs or "browser has been closed" in logs:
        return (
            FailureType.ENVIRONMENT_ISSUE,
            1.0,
            "Detected 'TargetClosedError' or browser crash",
        )

    # 3. Assertion Failures
    # Look for "expect(received).toBe(expected)" pattern
    if "expect(" in logs and "received" in logs:
        return (
            FailureType.ASSERTION_FAILED,
            1.0,
            "Detected 'expect(...)' assertion failure",
        )

    # 4. Locator Issues
    # If Playwright helps us by listing available elements, it's likely a drift
    if "Error: strict mode violation" in logs:
        return (
            FailureType.LOCATOR_DRIFT,
            0.9,
            "Strict mode violation: multiple elements match selector",
        )

    # If it says "locator resolved to 0 elements", it might be missing or drifted
    if "locator resolved to 0 elements" in logs:
        # If we see suggestions like "Did you mean..." it's a drift
        if "Did you mean" in logs:
            return (
                FailureType.LOCATOR_DRIFT,
                0.8,
                "Locator failed but Playwright suggested content alternative",
            )
        return (FailureType.LOCATOR_NOT_FOUND, 0.7, "Locator resolved to 0 elements")

    return (FailureType.UNKNOWN, 0.0, "No specific regex pattern matched")


def analyze_and_plan(test_file, code, evidence: Evidence) -> HealingDecision:
    """Ask LLM to analyze failure and plan a fix, guided by heuristics."""

    # Run Heuristics First
    h_type, h_conf, h_reason = classify_failure_heuristic(evidence.error_log)

    system_prompt = f"""You are an Expert QA Automation Engineer.
Analyze the broken Playwright test and the error log.

HEURISTIC DIAGNOSIS:
The system has preliminarily analyzed the logs:
- Type: {h_type.value}
- Confidence: {h_conf}
- Reason: {h_reason}

YOUR GOAL:
1. Verify this diagnosis (or correct it if you see strong evidence otherwise).
2. Explain your reasoning step-by-step.
3. Propose a specific code fix.

OUTPUT FORMAT:
You MUST return a valid JSON object matching this schema:
{{
    "failure_type": "LOCATOR_DRIFT" | "TIMEOUT" | "ASSERTION_FAILED" | "ENVIRONMENT_ISSUE" | "POTENTIAL_APP_DEFECT",
    "failure_summary": "Short description of failure",
    "hypothesis": "Why the fix will work",
    "confidence_score": 0.95,
    "reasoning_steps": ["step 1", "step 2"],
    "action_taken": {{
        "original_code": "EXACT contiguous block of code to be replaced. MUST MATCH FILE EXACTLY including whitespace. Do NOT skip lines between edits.",
        "fixed_code":  "New contiguous block of code to insert.",
        "description": "What changed"
    }}
}}

IMPORTANT RULES:
1. 'original_code' must be a SINGLE CONTINUOUS block. Do not concatenante non-adjacent lines.
2. If multiple separate parts of the file need fixing, include the unchanged lines between them in 'original_code' and 'fixed_code' so the block is continuous.
3. Retain the same indentation style.
4. Focus on the PRIMARY cause of failure first."""

    user_prompt = f"""FILE: {test_file}

BROKEN CODE:
```typescript
{code}
```

ERROR LOGS:
{evidence.error_log[:2000]}"""

    client = get_client()
    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        raw_content = response.choices[0].message.content
        json_content = extract_json_block(raw_content)
        data = json.loads(json_content, strict=False)

        # If heuristic confidence is high (>0.8), prefer heuristic type unless LLM overrides with strong reasoning
        final_type = data.get("failure_type", FailureType.UNKNOWN)
        if h_conf > 0.8 and final_type == FailureType.UNKNOWN:
            final_type = h_type

        # Prepare Action Data (Sanitize if LLM returns list of strings for code)
        action_data = data.get("action_taken", {})
        if isinstance(action_data.get("original_code"), list):
            action_data["original_code"] = "\n".join(action_data["original_code"])
        if isinstance(action_data.get("fixed_code"), list):
            action_data["fixed_code"] = "\n".join(action_data["fixed_code"])

        return HealingDecision(
            test_file=test_file,
            failure_type=final_type,
            failure_summary=data.get("failure_summary", "No summary provided"),
            evidence=evidence,
            hypothesis=data.get("hypothesis", "No hypothesis"),
            confidence_score=data.get("confidence_score", 0.0),
            reasoning_steps=data.get("reasoning_steps", []),
            action_taken=HealingAction(**action_data),
        )

    except Exception as e:
        print(f"LLM Analysis Error: {e}")
        return HealingDecision(
            test_file=test_file,
            failure_type=FailureType.UNKNOWN,
            failure_summary=f"Agent failed to analyze: {str(e)}",
            evidence=evidence,
            hypothesis="Fallback: Manual intervention needed",
            confidence_score=0.0,
            reasoning_steps=["LLM call failed"],
            action_taken=HealingAction(
                original_code="", fixed_code="", description="No action"
            ),
        )


def apply_fix(file_path, current_code, decision: HealingDecision):
    """Apply the code change described in the decision with robust matching."""
    target = decision.action_taken.original_code
    replacement = decision.action_taken.fixed_code

    if not target or not replacement:
        return current_code

    # 1. Try Exact Match
    if target in current_code:
        return current_code.replace(target, replacement)

    # 2. Try Normalized Match (Ignore leading/trailing whitespace per line)
    # This helps if the LLM messes up indentation
    def normalize_lines(text):
        return [line.strip() for line in text.splitlines() if line.strip()]

    target_lines = normalize_lines(target)
    code_lines = current_code.splitlines()

    # Simple sliding window search
    for i in range(len(code_lines) - len(target_lines) + 1):
        window = [line.strip() for line in code_lines[i : i + len(target_lines)]]
        # Check if window matches target lines (ignoring empty lines in code if needed)
        # For strictness, we'll just compare stripped content
        if window == target_lines:
            # Found it! Replace these lines
            # Note: We replace the *original* lines from the file (preserving their indentation if possible?
            # No, we'll likely use the indentation of the first line)

            # Construct replacement
            # Calculate indentation of the first matched line
            first_line_idx = i
            base_indent = code_lines[first_line_idx][
                : len(code_lines[first_line_idx])
                - len(code_lines[first_line_idx].lstrip())
            ]

            # Indent the replacement lines
            replacement_lines = replacement.splitlines()
            indented_replacement = []
            for r_line in replacement_lines:
                indented_replacement.append(base_indent + r_line.lstrip())

            new_code_lines = (
                code_lines[:i]
                + indented_replacement
                + code_lines[i + len(target_lines) :]
            )
            return "\n".join(new_code_lines)

    print(
        f"WARNING: Target code not found in file (even after normalization).\nTarget:\n{target}"
    )
    return current_code


def emit_artifacts(decision: HealingDecision, timeline: ExecutionTimeline):
    """Write the decision and timeline to JSON files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Healing Decision
    decision_filename = f"healing_decision_{timestamp}.json"
    decision_path = os.path.join(ARTIFACTS_DIR, decision_filename)
    with open(decision_path, "w") as f:
        f.write(decision.to_json())

    # 2. Timeline
    timeline_filename = f"execution_timeline_{timestamp}.json"
    timeline_path = os.path.join(ARTIFACTS_DIR, timeline_filename)
    with open(timeline_path, "w") as f:
        f.write(timeline.to_json())

    print(f"  -> Artifacts saved:\n     {decision_path}\n     {timeline_path}")


def attempt_healing(test_file, max_retries=1):
    """Orchestrate the healing pipeline."""
    timeline = ExecutionTimeline()
    timeline.add_step("Start", f"Healing session started for {test_file}")

    validated_path = validate_file_path(test_file)
    if not os.path.exists(validated_path):
        msg = f"Error: File not found {validated_path}"
        timeline.add_step("Error", msg)
        return msg

    print(f"\n--- Starting Healing Session: {test_file} ---")

    # 1. Initial Run
    result = run_test(validated_path)
    if result.returncode == 0:
        timeline.add_step("InitialRun", "Test passed, no healing needed")
        return "Test passed (No healing needed)."

    timeline.add_step(
        "FailureDetected",
        f"Initial test run failed with return code {result.returncode}",
    )

    # Read code
    with open(validated_path, "r") as f:
        current_code = f.read()

    # 2. Loop
    for attempt in range(max_retries):
        print(f"\nAttempt {attempt + 1}/{max_retries}")
        timeline.add_step("HealingAttempt", f"Starting attempt {attempt + 1}")

        # Gather Evidence
        evidence = gather_evidence(validated_path, result)
        timeline.add_step(
            "EvidenceCollected", "Logs and screenshot (if available) collected"
        )

        # Reason & Plan
        decision = analyze_and_plan(validated_path, current_code, evidence)
        print(f"  diagnosis: {decision.failure_type}")
        print(f"  hypothesis: {decision.hypothesis}")

        timeline.add_step(
            "AnalysisComplete",
            f"Diagnosed as {decision.failure_type}. Hypothesis: {decision.hypothesis}",
        )

        # Act
        new_code = apply_fix(validated_path, current_code, decision)

        if new_code == current_code:
            decision.verification_log = "Could not apply fix (code mismatch)"
            timeline.add_step(
                "ActionFailed",
                "Proposed fix could not be applied (target code not found)",
            )
            emit_artifacts(decision, timeline)
            continue

        timeline.add_step(
            "SelectorUpdated", f"Applied fix: {decision.action_taken.description}"
        )

        # Write new code
        with open(validated_path, "w") as f:
            f.write(new_code)

        # Verify
        verify_result = run_test(validated_path)
        decision.verification_passed = verify_result.returncode == 0
        decision.verification_log = (
            verify_result.stdout
            if verify_result.returncode == 0
            else verify_result.stderr
        )

        if decision.verification_passed:
            timeline.add_step("Verification", "Test passed on re-run")
        else:
            timeline.add_step("Verification", "Test failed on re-run")

        # Report
        emit_artifacts(decision, timeline)

        if decision.verification_passed:
            return f"\nSUCCESS: Test healed! \nReasoning: {decision.hypothesis}"

        # Prepare for next loop
        current_code = new_code
        result = verify_result
        timeline.add_step("Retry", "Preparing for next retry attempt")

    timeline.add_step(
        "HealingFailed", f"Exhausted {max_retries} attempts without success"
    )
    return "Healing failed to make test pass."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.agents.healer <test_file>")
        sys.exit(1)
    print(attempt_healing(sys.argv[1]))
