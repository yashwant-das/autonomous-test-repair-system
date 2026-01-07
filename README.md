# LM Studio QA Agent

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
│   ├── utils/           # Shared utilities (LLM client, Browser, Validation)
│   └── app.py           # Unified Gradio UI
├── tests/
│   ├── generated/       # Storage for generated .spec.ts files
│   └── screenshots/     # Storage for Vision Agent debug screenshots
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies (Playwright)
├── playwright.config.ts # Playwright configuration
├── tsconfig.json        # TypeScript configuration
├── ENV_VARIABLES.md     # Environment variables documentation
└── README.md
```

## Setup

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
`saucedemo_login_with_standard_user_20240107_230500.spec.ts`

### Running Agents Individually

You can also run specific agents directly from the command line:

```bash
python src/agents/healer.py tests/generated/broken_example.spec.ts
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
- **Command**: `python src/agents/healer.py tests/generated/broken_example.spec.ts`
- **Goal**: Automatically repairs incorrect selectors and labels by analyzing Playwright error logs.
- **Trial**: To see it in action, purposefully introduce mistakes into the locator IDs or button names in the script and
  watch the agent heal them!

## Configuration

You can customize the LLM settings by using environment variables. Create a `.env` file in the project root or set the following variables:

- `LM_STUDIO_URL`: Defaults to `http://localhost:1234/v1`
- `LM_STUDIO_API_KEY`: Defaults to `lm-studio`
- `DEFAULT_MODEL`: Defaults to `local-model`
- `VISION_MODEL`: Defaults to `local-model`

For detailed information about all environment variables, see [ENV_VARIABLES.md](ENV_VARIABLES.md).

## Technical Details

### Test Configuration
- **Playwright**: Configured via `playwright.config.ts` with retry logic, HTML reporting, and screenshot/video capture on failure
- **TypeScript**: Configured via `tsconfig.json` with strict type checking
- Tests are automatically organized with timestamp-based naming

### Security
- Input validation prevents malicious URLs and path traversal attacks
- File operations are restricted to allowed directories
- Subprocess calls use proper sanitization
