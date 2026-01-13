# 🎬 Killer Demo Guide: LM Studio QA Agent

> Follow this script to showcase the "Senior QA Engineer" intelligence of this agent in under 2 minutes.

## 🏁 Preparation

1. Ensure LM Studio/OpenAI is running.
2. Run the setup script:
   ```bash
   python scripts/setup_demo.py
   ```
   _This creates a "dirty" test case that simulates common flaky behavior._

---

## 🎭 The Script

### 1. The Setup (0:00 - 0:30)

- **What to say**: "Most AI agents are black boxes. I built an agent that prioritizes **Explainability**. Here's a standard Playwright test that fails due to a locator drift—something that usually costs hours of debugging."
- **What to do**: Open `tests/generated/demo_broken.spec.ts` and show the incorrect selector.

### 2. The Healing Action (0:30 - 1:00)

- **What to say**: "I'll upload this to the Self-Healer dashboard. My agent won't just try to fix it; it will first categorize the failure using **Deterministic Heuristics** to ensure we're not hallucinating."
- **What to do**:
  - Open the UI (`python src/app.py`).
  - Upload the file.
  - Click **Heal Test**.

### 3. The "Wow" Moment (1:00 - 1:45)

- **What to say**: "Look at the **Execution Timeline**. You can see the agent correctly identified a `TIMEOUT` with **100% confidence** before it even consulted the LLM. Now, it's synthesizing a fix based on the DOM context."
- **Point to**:
  - The **Timeline** steps (🧠 Analysis, 🛠️ Fix).
  - The **Decision JSON** (Show the `hypothesis` and `reasoning_steps`).

### 4. The Result (1:45 - 2:00)

- **What to say**: "The test passes, but more importantly, we have a complete audit trail of the decision. We’ve turned a 'flaky test' into a solved, documented problem."
- **What to do**: Show the "TEST PASSED" message and the generated artifacts in `tests/artifacts/`.

---

## 💎 Bonus Highlights for Recruiters

- **Resilience**: "I implemented fuzzy matching for code replacement to handle imperfect LLM output."
- **Safety**: "The agent runs in a sandboxed directory with strict path validation."
- **Efficiency**: "By using regex heuristics first, we reduce LLM token usage and increase reliability."
