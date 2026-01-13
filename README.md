# 🤖 LM Studio QA Agent

> **An Intelligent, Self-Healing, and Explainable Automated QA System**

[![Status](https://img.shields.io/badge/Status-Beta-orange)](https://github.com/yashwant-das/lmstudio-qa-agent)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://github.com/yashwant-das/lmstudio-qa-agent)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green)](https://playwright.dev/)

## 🚨 The Problem: "Flaky Tests exist because Debugging is Hard"

Modern QA automation is broken. When a test fails, engineers spend hours digging through logs to answer 3 simple questions:

1. **Is it a real bug?** (Or just network fluff?)
2. **What changed?** (Locator drift? CSS update?)
3. **How do I fix it?**

Most "AI" solutions are black boxes that randomly try things until green. **We believe in Explainability.**

## 💡 The Solution: Intelligent Healing

The **LM Studio QA Agent** doesn't just "fix" tests—it behaves like a Senior QA Engineer:

1. **Investigates**: Runs tests and captures high-fidelity evidence (logs, DOM snippets).
2. **Diagnoses**: Uses **Deterministic Heuristics** (Regex) for instant confidence 1.0 matches (`TIMEOUT`, `ASSERTION_FAIL`).
3. **Reasoning**: Consults an LLM (guided by the heuristics) to plan a fix.
4. **Explains**: Outputs a structured **Execution Timeline** and **Decision JSON** proving _why_ it made the change.

---

## ✨ Key Features

### 🧠 Failure Intelligence Layer

Unlike naive agents, we don't guess.

- **Enhanced Heuristics**: Deterministically identifies network errors (404/500), JavaScript runtime errors, and locator drift.
- **Improved Evidence**: Automatically finds and links Playwright screenshots from `test-results` to the healing decision.
- **Customizable Prompts**: All LLM system instructions are externalized in the `prompts/` directory for easy tweaking.

### 🔍 Explainable Artifacts

Every healing attempt generates:

- `healing_decision_*.json`: The brain dump (Diagnosis, Hypothesis, Fix).
- `execution_timeline_*.json`: Step-by-step audit trail.

### 🖥️ Self-Healing Dashboard

A minimal, powerful UI to visualize the agent's brain:

- **Timeline View**: Watch the agent think in real-time steps.
- **Decision Inspector**: View the raw JSON data behind the fix.

---

## 📈 Understanding Confidence Scores

The agent assigns a **Confidence Score (0.0 - 1.0)** to every diagnosis:

- **1.0 (Certain)**: The failure matched a **Deterministic Heuristic** (Regex). No guessing involved.
- **0.8 - 0.9 (Strong)**: The LLM identified the issue with high certainty based on logs and code context.
- **< 0.7 (Low)**: The failure is ambiguous; the agent is proposing a "best-guess" fix that requires closer human review.

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
npm install           # Installs Playwright & Quality Control tools
pip install -r requirements.txt
playwright install
```

### Run the Demo

1. **Setup a Broken Test**:

   ```bash
   python scripts/setup_demo.py
   ```

   _(Creates `tests/generated/demo_broken.spec.ts` with an intentional bug)_

2. **Launch the UI**:

   ```bash
   python src/app.py
   ```

3. **Heal It**:
   - Go to **Self-Healer** tab.
   - Upload `tests/generated/demo_broken.spec.ts`.
   - Click **Heal Test**.
   - Watch the **Timeline** and **Decision** populate!

## 🏗️ Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for a deep dive into the **Monitor -> Investigate -> Reason -> Act -> Report** pipeline.

## 🛠️ Customization: Prompts & Behavior

You can customize how the agents behave by editing the Markdown files in the `prompts/` directory:

- `generator.md`: Instructions for the Test Generator agent.
- `healer.md`: The strategy and JSON schema for the Self-Healer agent.
- `vision.md`: Instruction set for the Vision-based agent.

No code changes are required to tweak the agents' logic or output format!

## 🛠️ Development & Quality Control

We use a multi-layered linting and testing suite to ensure high-grade code quality.

### Commands

```bash
# Run all quality checks (JS, Python, Markdown)
npm run lint

# Run Python unit tests
npm run test:unit

# Auto-format all code (Prettier + Black)
npm run format
```

### Tooling Stack

- **TypeScript/JS**: Prettier + ESLint (v9 Flat Config) + Playwright Plugin
- **Python**: Black + isort + Flake8
- **Documentation**: Markdownlint
- **Automation**: Husky (Git Hooks) + lint-staged

## 🔮 Roadmap

- [ ] **Visual Diff**: Image comparison for UI regression.
- [ ] **Live Streaming**: Real-time websocket updates for the Timeline.
- [ ] **Multi-File Context**: Healing across dependent files/Page Objects.
