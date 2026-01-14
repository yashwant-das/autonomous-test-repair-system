# Autonomous Test Repair System

A modular, LLM-powered QA automation agent that generates and maintains Playwright tests.

## Features

- **Test Generation**: Scrapes web pages and generates runnable Playwright TypeScript tests.
- **Vision Agent**: Uses vision-capable LLMs (e.g., Qwen-VL) to understand UI from screenshots.
- **Self-Healing**: Automatically fixes broken tests by analyzing error logs and updating selectors.
- **Input Validation**: Comprehensive validation for URLs, file paths, and user inputs.
- **Error Handling**: Robust error handling with clear, user-friendly messages.
- **Standard UI**: Clean, minimal Gradio interface following standard design patterns.

## Project Structure

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
│   │   └── validation.py # Input validation utilities
│   └── app.py           # Unified Gradio UI
├── tests/
│   ├── generated/       # Storage for generated .spec.ts files
│   └── screenshots/     # Storage for Vision Agent debug screenshots
├── test-results/        # Playwright test execution results
├── playwright-report/   # Playwright HTML test reports
├── Dockerfile           # Docker container configuration
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies (Playwright)
├── package-lock.json    # Node.js dependency lock file
├── playwright.config.ts # Playwright configuration
├── tsconfig.json        # TypeScript configuration
├── .env                 # Environment variables (create from ENV_VARIABLES.md)
├── ENV_VARIABLES.md     # Environment variables documentation
├── DOCKER.md            # Docker workflow guide
└── README.md            # This file
```

## Setup

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker. The project includes a `Dockerfile` that sets up the complete environment.

```bash
# Build the Docker image
docker build -t qa-agent .

# Run the container
docker run -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  qa-agent
```

Access the Gradio interface at `http://localhost:7860`.

**For detailed Docker instructions**, including:
- Building and running containers
- Volume mounts for development
- Manual debugging and healing workflows
- Container management commands
- Troubleshooting tips

See [DOCKER.md](DOCKER.md) for complete documentation.

### Option 2: Local Installation

1. **Install Python Dependencies**:
   > **Recommendation**: Use **Python 3.12** or **3.11**. These versions have pre-compiled wheels for all dependencies,
   ensuring a fast and error-free installation.
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js Dependencies**:
   ```bash
   npm install
   npx playwright install
   ```

3. **Configure LM Studio**:
    - Ensure LM Studio is running.
    - Load desired models (e.g., `qwen3-coder-30b`, `qwen3-vl-30b`).
    - Models should be available at `http://localhost:1234/v1`.
    - See [ENV_VARIABLES.md](ENV_VARIABLES.md) for detailed configuration options.

## Usage

Run the main application:

```bash
# Recommended execution
python src/app.py
```

This will launch a Gradio interface (http://127.0.0.1:7860) where you can generate, run, and heal tests.

### Test Naming Convention

Generated tests follow a professional, organized naming scheme:
`[domain]_[description]_[timestamp].spec.ts`

**Example**:
`saucedemo_login_with_standard_user_20250108_143000.spec.ts`

### Running Agents Individually

You can also run specific agents directly from the command line:

```bash
python -m src.agents.healer tests/generated/broken_example.spec.ts
```

## Example Scenarios

### 1. Test Generator (Form Authentication)

- **URL**: `https://the-internet.herokuapp.com/login`
- **Scenario**: `Login with tomsmith and SuperSecretPassword!. Verify the success message appears.`
- **Goal**: Proves the agent can handle standard HTML forms and success notifications.

### 2. Test Generator (Dynamic React Apps)

- **URL**: `https://demo.playwright.dev/todomvc/`
- **Scenario**: `Add a todo item named 'Buy Milk'. Verify it appears in the list.`
- **Goal**: Demonstrates capabilities with heavily dynamic, client-side rendered JavaScript apps.

### 3. Test Generator (Real-world Search)

- **URL**: `https://www.wikipedia.org`
- **Scenario**:
  `Type 'AI' in the search input and press Enter. Verify that the URL contains 'Artificial_intelligence' and the main heading (h1) says 'Artificial intelligence'.`
- **Goal**: Validates search interactions and multiple verification steps on professional sites.

### 4. Vision Agent

- **URL**: `https://www.saucedemo.com`
- **Scenario**: `Login with standard_user / secret_sauce`
- **Goal**: Uses visual analysis to identify elements without relying solely on HTML source.

### 5. Self-Healer

- **Input**: A broken test file like [broken_example.spec.ts](tests/generated/broken_example.spec.ts)
- **Command**: `python -m src.agents.healer tests/generated/broken_example.spec.ts`
- **Goal**: Automatically repairs incorrect selectors and labels by analyzing Playwright error logs.
- **Trial**: To see it in action, purposefully introduce mistakes into the locator IDs or button names in the script and
  watch the agent heal them!

## Configuration

### Environment Variables

You can customize the LLM settings by using environment variables. Create a `.env` file in the project root (see [ENV_VARIABLES.md](ENV_VARIABLES.md) for template):

- `LM_STUDIO_URL`: Defaults to `http://localhost:1234/v1`
- `LM_STUDIO_API_KEY`: Defaults to `lm-studio`
- `DEFAULT_MODEL`: Defaults to `local-model`
- `VISION_MODEL`: Defaults to `local-model`

**For complete environment variable documentation**, including descriptions, defaults, and usage examples, see [ENV_VARIABLES.md](ENV_VARIABLES.md).

## Technical Details

### Test Configuration
- **Playwright**: Configured via `playwright.config.ts` with retry logic, HTML reporting, and screenshot/video capture on failure
- **TypeScript**: Configured via `tsconfig.json` with strict type checking
- Tests are automatically organized with timestamp-based naming
- Test results are stored in `test-results/` directory
- HTML reports are generated in `playwright-report/` directory

### Docker Configuration
- **Base Image**: Uses official Playwright Python image (`mcr.microsoft.com/playwright/python`)
- **Node.js**: Installed separately (v20.x) as it's not included in the base image
- **Port**: Exposes port 7860 for Gradio interface
- **Environment**: Configured to listen on all interfaces (`0.0.0.0`) for container access

For detailed Docker workflows, see [DOCKER.md](DOCKER.md).

### Security
- Input validation prevents malicious URLs and path traversal attacks
- File operations are restricted to allowed directories
- Subprocess calls use proper sanitization

## Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** (this file): Overview, setup, and usage
- **[DOCKER.md](DOCKER.md)**: Complete Docker workflow guide
- **[ENV_VARIABLES.md](ENV_VARIABLES.md)**: Environment variable reference
