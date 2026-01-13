# 🤖 LM Studio QA Agent

> **An Intelligent, Self-Healing, and Explainable Automated QA System**

[![Status](https://img.shields.io/badge/Status-Beta-orange)]()
[![Python](https://img.shields.io/badge/Python-3.14-blue)]()
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green)]()

## 🚨 The Problem: "Flaky Tests exist because Debugging is Hard"

Modern QA automation is broken. When a test fails, engineers spend hours digging through logs to answer 3 simple questions:

1.  **Is it a real bug?** (Or just network fluff?)
2.  **What changed?** (Locator drift? CSS update?)
3.  **How do I fix it?**

Most "AI" solutions are black boxes that randomly try things until green. **We believe in Explainability.**

## 💡 The Solution: Intelligent Healing

The **LM Studio QA Agent** doesn't just "fix" tests—it behaves like a Senior QA Engineer:

1.  **Investigates**: Runs tests and captures high-fidelity evidence (logs, DOM snippets).
2.  **Diagnoses**: Uses **Deterministic Heuristics** (Regex) for instant confidence 1.0 matches (`TIMEOUT`, `ASSERTION_FAIL`).
3.  **Reasons**: Consults an LLM (guided by the heuristics) to plan a fix.
4.  **Explains**: Outputs a structured **Execution Timeline** and **Decision JSON** proving _why_ it made the change.

---

## ✨ Key Features

### 🧠 Failure Intelligence Layer

Unlike naive agents, we don't guess.

- **Regex Heuristics**: Instantly identifies `TimeoutError`, `TargetClosed`, `expect()` failures.
- **Hybrid Confidence**: High confidence for known patterns, lower confidence for LLM hypotheses.
- **Sanitization**: Robustly handles imperfect LLM code output (fuzzy matching, whitespace normalization).

### 🔍 Explainable Artifacts

Every healing attempt generates:

- `healing_decision_*.json`: The brain dump (Diagnosis, Hypothesis, Fix).
- `execution_timeline_*.json`: Step-by-step audit trail.

### 🖥️ Self-Healing Dashboard

A minimal, powerful UI to visualize the agent's brain:

- **Timeline View**: Watch the agent think in real-time steps.
- **Decision Inspector**: View the raw JSON data behind the fix.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js & Playwright
- Local LLM (LM Studio) or OpenAI API Key

### Installation

```bash
git clone https://github.com/yourusername/lmstudio-qa-agent.git
cd lmstudio-qa-agent
pip install -r requirements.txt
playwright install
```

### Run the Demo

1.  **Setup a Broken Test**:

    ```bash
    python scripts/setup_demo.py
    ```

    _(Creates `tests/generated/demo_broken.spec.ts` with an intentional bug)_

2.  **Launch the UI**:

    ```bash
    python src/app.py
    ```

3.  **Heal It**:
    - Go to **Self-Healer** tab.
    - Upload `tests/generated/demo_broken.spec.ts`.
    - Click **Heal Test**.
    - Watch the **Timeline** and **Decision** populate!

---

## 🏗️ Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for a deep dive into the **Monitor -> Investigate -> Reason -> Act -> Report** pipeline.

## 🔮 Roadmap

- [ ] **Visual Diff**: Image comparison for UI regression.
- [ ] **Live Streaming**: Real-time websocket updates for the Timeline.
- [ ] **Multi-File Context**: Healing across dependent files/Page Objects.
