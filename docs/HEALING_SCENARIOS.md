# Healing Scenarios: Showcase of Intelligence

> This document details real-world scenarios where the **Healer Agent** demonstrates its reasoning capabilities.

---

## 1. The "Locator Drift" Scenario

**Scenario**: A developer changes a button's `id` from `#submit-login` to `#login-button-v2`.

- **Heuristic Detection**: Playwright fails with a `TimeoutError`. The agent scans the logs and finds "locator resolved to 0 elements".
- **LLM Reasoning**: The agent looks at the failing line of code and the current DOM state. It calculates a **0.8 confidence** score because it identifies a button with similar text ("Login") but a different ID.
- **The Fix**: It automatically patches the test to use the new ID or a more robust text-based selector.

## 2. The "Dynamic Content" Scenario

**Scenario**: A test expects a success message "Saved Successfully!", but the app now returns "Changes saved!".

- **Heuristic Detection**: The test fails an assertion.
- **LLM Reasoning**: The agent reads the assertion log: `expected: "Saved Successfully!", received: "Changes saved!"`. It realizes the intent (verifying success) is still met, but the copy has changed.
- **The Fix**: It updates the `expect(...).toContainText()` call to match the new string.

## 3. The "Network Flakiness" Scenario

**Scenario**: A test fails because a 3rd party API returned a `500 Internal Server Error` during the run.

- **Heuristic Detection**: The agent uses Regex to find `500` in the Playwright logs.
- **Intelligence**: Instead of trying to "fix" the code, the agent correctly identifies this as a **POTENTIAL_APP_DEFECT** with **0.8 confidence**.
- **Operational Insight**: The agent reports that the code is likely fine, but the environment is unstable, saving the developer from chasing "ghost" bugs in the test logic.

## 4. The "Race Condition" Scenario

**Scenario**: A button is present in the DOM but not yet clickable because a loading overlay is still active.

- **Heuristic Detection**: `TimeoutError` while waiting for the element to be "visible and stable".
- **LLM Reasoning**: The agent identifies the presence of a spinner/loader in the DOM snippet.
- **The Fix**: It inserts an `await page.waitForSelector('.spinner', { state: 'hidden' })` before the interaction, implementing a professional "waiting" strategy.

---

### Try it Yourself

Purposefully break any generated script (change a locator, delete a character in a selector) and run it through the **Self-Healer** tab in the UI.
