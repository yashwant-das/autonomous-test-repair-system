# Architecture & Design

> **Single Source of Truth** for the Explainable QA Agent.
> Last Updated: Phase 1 A

## 1. Problem Statement

Automated test healing is often a "black box." When a test breaks and is automatically fixed, engineers (and recruiters) ask:

1.  _Why_ did it fail?
2.  _Why_ did the agent choose this specific fix?
3.  _Can I trust_ that this fix is correct and not just a lucky guess?

The current system repairs tests but fails to explain its reasoning. It lacks **explainability**, **intent-awareness**, and **provenance**.

**The Goal:** Build a system where every automated repair is accompanied by a structured `HealingDecision` that provides evidence, reasoning, and verification proof.

---

## 2. Agent Responsibilities

The system consists of three primary agents, each with strict boundaries:

### A. Generator Agent (`src/agents/generator.py`)

- **Input:** URL, User Story (Text).
- **Responsibility:** Generates the _initial_ Playwright TypeScript test.
- **Method:** DOM-based analysis (primary) or Vision-based (secondary).
- **Output:** A runnable `.spec.ts` file in `tests/generated/`.

### B. Vision Agent (`src/agents/vision.py`)

- **Input:** URL, Instruction.
- **Responsibility:** Provides visual understanding when DOM analysis is insufficient.
- **Method:** Captures screenshots, uses Vision LLM to interpret UI layout and user intent.
- **Output:** Generates test code based on visual cues (e.g., "blue button in top right").

### C. Healer Agent (`src/agents/healer.py`) — **The Focus of Phase 1**

- **Input:** Path to a failing `.spec.ts` file.
- **Responsibility:** Diagnoses failure, hypothesizes root cause, gathers evidence, patches the code, and verifies the fix.
- **Key Constraint:** Must emit a `HealingDecision` artifact for every attempt.
- **Output:**
  1.  Patched test file.
  2.  `HealingDecision` JSON (Evidence + Reasoning).

---

## 3. Healing Decision Pipeline

The Healer Agent operates in a strict pipeline. It does not "think" in unstructured loops.

1.  **Failure Detection (Monitor)**
    - Runs the test via Playwright.
    - Parses `stderr` / `stdout` for specific error codes (e.g., `TimeoutError`, `TargetClosedError`).

2.  **Evidence Collection (Investigate)**
    - **Logs:** Extracts the exact error message.
    - **DOM:** Captures the current page state (if accessible).
    - **Visual:** Captures a screenshot at the moment of failure.

3.  **Root Cause Analysis (Reason)**
    - Classifies failure: `LOCATOR_DRIFT`, `TIMEOUT`, `LOGIC_ERROR`, etc.
    - Formulates a hypothesis (e.g., "ID changed from `#submit` to `#btn-submit`").

4.  **Remediation (Act)**
    - Proposes a specific code change (e.g., `page.locator('#old')` -> `page.getByTestId('new')`).
    - **Crucial:** Logs _why_ this change was selected.

5.  **Verification (Confirm)**
    - Re-runs the _only_ the patched test.
    - Records the result (Pass/Fail).

6.  **Artifact Emission (Report)**
    - Writes `healing_decision_[timestamp].json`.
    - Writes `execution_timeline_[timestamp].json`.

---

## 4. Determinism & Safety Guarantees

To ensure the agent is production-credible and not "flaky AI demoware":

1.  **Bounded Execution:**
    - Max 2 healing attempts per test run.
    - No infinite retry loops.

2.  **Deterministic Data Models:**
    - All decisions are stored in strict JSON schemas.
    - No free-form prose for machine-readable fields.

3.  **Sandboxed Filesystem:**
    - Agent only modifies files in `tests/generated/`.
    - Cannot modify core logic in `src/`.

4.  **Human-in-the-Loop Capable:**
    - The system is designed so a human can review `HealingDecision` JSONs before merging changes (if integrated into CI/CD).
