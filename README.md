# 🤖 Autonomous Test Repair System

> **An Intelligent, Self-Healing, and Explainable Automated QA System**

[![Status](https://img.shields.io/badge/Status-Beta-orange)](https://github.com/yashwant-das/autonomous-test-repair-system)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green)](https://playwright.dev/)

## 🚨 The Problem: "Flaky Tests exist because Debugging is Hard"

Modern QA automation is broken. When a test fails, engineers spend hours digging through logs to answer 3 simple questions:

1. **Is it a real bug?** (Or just network fluff?)
2. **What changed?** (Locator drift? CSS update?)
3. **How do I fix it?**

Most "AI" solutions are black boxes. **We believe in Explainability.**

## 💡 The Solution: Intelligent Healing

The **Autonomous Test Repair System** doesn't just "fix" tests—it behaves like a Senior QA Engineer:

1. **Investigates**: Runs tests and captures high-fidelity evidence (logs, DOM snippets, screenshots).
2. **Diagnoses**: Uses **Enhanced Heuristics** for instant detection of timeouts, network errors (404/500), and JS crashes.
3. **Reasoning**: Consults an LLM (guided by heuristics and externalized prompts) to plan a fix.
4. **Explains**: Outputs structured **Execution Timelines** and **Decision JSON** proving _why_ it made the change.

---

## 🌟 The "Wow" Factor

What makes this project stand out for recruiters and developers?

- **Zero-Black-Box Reasoning**: Every fix comes with a `HealingDecision` JSON. You can literally "read the agent's mind."
- **Hybrid Intelligence**: We don't waste LLM tokens on obvious errors. Our **Deterministic Heuristics** handle the "low-hanging fruit" with 1.0 confidence.
- **Enterprise-Grade DX**: A complete quality control pipeline (ESLint 9, Flake8, Husky, lint-staged) ensures a professional developer experience from day one.
- **Vision-Augmented**: When the DOM is too complex, the **Vision Agent** looks at screenshots to understand the UI layout, just like a human would.

---

## ✨ Features

- **Test Generation**: Scrapes web pages and generates runnable Playwright TypeScript tests.
- **Vision Agent**: Uses vision-capable LLMs (e.g., Qwen-VL) to understand UI from screenshots.
- **Self-Healing**: Automatically fixes broken tests by analyzing error logs and updating selectors.
- **Enhanced Heuristics**: Deterministically identifies network errors, JavaScript runtime errors, and locator drift.
- **Customizable Prompts**: All LLM system instructions are externalized in the `prompts/` directory for easy tweaking.
- **Input Validation**: Comprehensive validation for URLs, file paths, and user inputs.
- **Standard UI**: Clean, minimal Gradio interface following standard design patterns.

---

## 📈 Understanding Confidence Scores

The agent assigns a **Confidence Score (0.0 - 1.0)** to every diagnosis:

- **1.0 (Certain)**: The failure matched a **Deterministic Heuristic** (Regex). No guessing involved.
- **0.8 - 0.9 (Strong)**: The LLM identified the issue with high certainty based on logs and code context.
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

1. **Form Authentication**: [The Internet Login](https://the-internet.herokuapp.com/login). Proves handling of standard forms.
2. **Dynamic React Apps**: [TodoMVC](https://demo.playwright.dev/todomvc/). Demonstrates client-side rendered app support.
3. **Real-world Search**: [Wikipedia AI Search](https://www.wikipedia.org). Validates multi-step verification.
4. **Vision Agent**: [SauceDemo Vision](https://www.saucedemo.com). Uses screenshots to identify elements.
5. **Self-Healer**: Automatically repairs incorrect selectors by analyzing logs. See [HEALING_SCENARIOS.md](docs/HEALING_SCENARIOS.md) for a list of common "heals."

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
