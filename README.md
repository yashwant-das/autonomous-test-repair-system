# Autonomous Test Repair System

> **An Intelligent, Self-Healing, and Explainable Automated QA System**

[![Status](https://img.shields.io/badge/Status-Beta-orange)](https://github.com/yashwant-das/autonomous-test-repair-system)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green)](https://playwright.dev/)

## 🚨 Problem Statement

Modern QA automation faces significant scalability challenges. When tests fail, engineering teams invest substantial time analyzing logs to distinguish between:

1. **Application Defects**: Genuine regressions or bugs.
2. **Environment Issues**: Network latency or service unavailability.
3. **Test Flakiness**: Locator drift or race conditions.

Many existing AI-based solutions operate as "black boxes," automatically patching code without providing insight into the decision-making process. **This lack of explainability inhibits trust and complicates long-term maintenance.**

## 💡 Solution Overview

The **Autonomous Test Repair System** is an intelligent agent designed to reduce test maintenance overhead through automated diagnosis and remediation. It emulates senior-level QA capabilities by executing a four-stage pipeline:

1. **Investigate**: Captures high-fidelity evidence (logs, DOM trees, screenshots) during test execution.
2. **Diagnose**: Utilizes **Deterministic Heuristics** for instant identification of common failures (timeouts, network errors) and **LLM Analysis** for complex logic.
3. **Reason**: Synthesizes evidence to formulate a remediation plan, documented in a structured JSON artifact.
4. **Act & Explain**: Applies the fix and generates a detailed **Execution Timeline**, proving the validity of the change.

---

## 🚀 Key Differentiators

What sets this autonomous agent apart from standard test automation tools?

- **Transparent Reasoning**: Every fix includes a `HealingDecision` JSON artifact, allowing you to trace exactly why a specific change was made.
- **Hybrid Architecture**: Combines **Deterministic Heuristics** (Regex) for instant, low-cost error detection with **LLM Reasoning** for complex logic, optimizing both speed and cost.
- **Production-Ready Toolchain**: Ships with a proven quality control pipeline (ESLint 9, Flake8, Husky, lint-staged) to ensure maintainable, industry-standard code.
- **Multimodal Analysis**: When DOM scraping falls short, the **Vision Agent** analyzes screenshots to understand UI layout and context, mimicking human visual verification.

---

## ✨ Features

- **Automated Test Generation**: Analyzes DOM structures to generate robust Playwright TypeScript test suites.
- **Vision Agent**: Uses vision-capable LLMs (e.g., Qwen-VL) to understand UI from screenshots.
- **Self-Healing**: Automatically fixes broken tests by analyzing error logs and updating selectors.
- **Enhanced Heuristics**: Deterministically identifies network errors, JavaScript runtime errors, and locator drift.
- **Customizable Prompts**: All LLM system instructions are externalized in the `prompts/` directory for easy tweaking.
- **Input Validation**: Comprehensive validation for URLs, file paths, and user inputs.
- **Interactive Dashboard**: Centralized Gradio interface for managing test generation, vision context, and healing operations.

---

## 📈 Confidence Scoring System

The agent assigns a **Confidence Score (0.0 - 1.0)** to every diagnosis to facilitate risk assessment:

- **1.0 (Deterministic)**: The failure matched a verified pattern (e.g., specific error codes). No probabilistic reasoning involved.
- **0.8 - 0.9 (High)**: The LLM identified the root cause with strong evidence from logs and code context.
- **< 0.7 (Low)**: The failure is ambiguous; the agent is proposing a "best-guess" fix that requires human review.

---

## 🏗️ Project Structure

```text
.
├── src/
│   ├── agents/          # Agent logic (Generator, Vision, Healer)
│   │   ├── generator.py # Test generation agent
│   │   ├── healer.py    # Self-healing agent
│   │   └── vision.py    # Vision-based test generation
│   ├── models/          # Data models and schemas
│   │   └── healing_model.py # Healing artifacts & execution timeline models
│   ├── utils/           # Shared utilities
│   │   ├── browser.py   # Browser automation (Playwright)
│   │   ├── llm.py       # LLM client configuration
│   │   ├── prompt_loader.py # Externalized prompt management
│   │   └── validation.py # Input validation utilities
│   └── app.py           # Unified Gradio UI
├── prompts/             # Externalized LLM system instructions (.md)
├── docs/                # Extended documentation
│   ├── ARCHITECTURE.md  # Deep dive into the agentic pipeline
│   ├── DEMO_GUIDE.md    # Scripted guide for a killing demo
│   └── HEALING_SCENARIOS.md # Story-driven examples of healing logic
├── tests/
│   ├── unit_test_*.py   # Logic & heuristic unit tests
│   ├── generated/       # Storage for generated .spec.ts files
│   ├── artifacts/       # Healing decisions and execution timelines
│   └── screenshots/     # Storage for Vision Agent debug screenshots
├── test-results/        # Playwright test execution results
├── playwright-report/   # Playwright HTML test reports
├── Dockerfile           # Docker container configuration
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies (Playwright)
├── playwright.config.ts # Playwright configuration
└── README.md            # This file
```

---

## 🚀 Setup

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker.

```bash
# Build the Docker image
docker build -t qa-agent .

# Run the container
docker run -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  qa-agent
```

Access the Gradio interface at `http://localhost:7860`. See [DOCKER.md](DOCKER.md) for more info.

### Option 2: Local Installation

1. **Install Python Dependencies** (Python 3.11+ recommended):

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js Dependencies**:

   ```bash
   npm install
   npx playwright install
   ```

3. **Configure LM Studio**:
   Ensure LM Studio is running and models (e.g., Qwen-Coder, Qwen-VL) are loaded at `http://localhost:1234/v1`.

---

## 🛠️ Usage

### Launch the UI

```bash
python src/app.py
```

Go to `http://127.0.0.1:7860` to generate, run, and heal tests.

### Running Agents Individually

```bash
python -m src.agents.healer tests/generated/broken_example.spec.ts
```

---

## 🧪 Example Scenarios

### 1. Test Generator (Form Authentication)

- **URL**: [https://the-internet.herokuapp.com/login](https://the-internet.herokuapp.com/login)
- **Scenario**: Login with `tomsmith` and `SuperSecretPassword!`. Verify the success message appears.
- **Goal**: Proves the agent can handle standard HTML forms and success notifications.

### 2. Test Generator (Dynamic React Apps)

- **URL**: [https://demo.playwright.dev/todomvc/](https://demo.playwright.dev/todomvc/)
- **Scenario**: Add a todo item named 'Buy Milk'. Verify it appears in the list.
- **Goal**: Demonstrates capabilities with heavily dynamic, client-side rendered JavaScript apps.

### 3. Test Generator (Real-world Search)

- **URL**: [https://www.wikipedia.org](https://www.wikipedia.org)
- **Scenario**: Type 'AI' in the search input and press Enter. Verify that the URL contains 'Artificial_intelligence' and the main heading (h1) says 'Artificial intelligence'.
- **Goal**: Validates search interactions and multiple verification steps on professional sites.

### 4. Vision Agent

- **URL**: [https://www.saucedemo.com](https://www.saucedemo.com)
- **Scenario**: Login with `standard_user` / `secret_sauce`.
- **Goal**: Uses visual analysis to identify elements without relying solely on HTML source.

### 5. Self-Healer

- **Input**: A broken test file like `broken_example.spec.ts`.
- **Command**: `python -m src.agents.healer tests/generated/broken_example.spec.ts`
- **Goal**: Automatically repairs incorrect selectors and labels by analyzing Playwright error logs.
- **Deep Dive**: See [HEALING_SCENARIOS.md](docs/HEALING_SCENARIOS.md) for a detailed breakdown of how the agent resolves specific failures like Locator Drift, Network Flakiness, and Race Conditions.
- **Trial**: To see it in action, purposefully introduce mistakes into the locator IDs or button names in the script and watch the agent heal them!

---

## ⚙️ Configuration & Quality Control

### Environment Variables

See [ENV_VARIABLES.md](ENV_VARIABLES.md) for full documentation on `LM_STUDIO_URL`, `DEFAULT_MODEL`, etc.

### Customizable Prompts

Edit the files in `prompts/` to tweak agent behavior without changing code:

- `generator.md`, `healer.md`, `vision.md`.

### Development Commands

```bash
npm run lint      # Run all quality checks
npm run test:unit # Run Python unit tests
npm run format    # Auto-format all code
```

### Tooling Stack

- **TypeScript/JS**: Prettier + ESLint (v9 Flat Config) + Playwright Plugin
- **Python**: Black + isort + Flake8
- **Documentation**: Markdownlint
- **Automation**: Husky (Git Hooks) + lint-staged

---

## 🔒 Security

- Input validation prevents malicious URLs and path traversal.
- File operations restricted to allowed directories.
- Subprocess calls use proper sanitization.

---

## 🏗️ Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for a deep dive into the **Monitor -> Investigate -> Reason -> Act -> Report** pipeline.
