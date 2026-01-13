# Docker Workflow Guide

This guide covers building and running the QA Agent in Docker, including manual debugging and healing workflows.

## Prerequisites

- Docker installed and running
- LM Studio running (Server ON, Port 1234)
- A broken test file in `tests/generated/` (e.g., `broken_example.spec.ts`)

## Building the Docker Image

Build the Docker image with the following command:

```bash
docker build -t qa-agent .
```

This creates a Docker image named `qa-agent` using the `Dockerfile` in the project root.

## Running the Container

### Basic Run

Run the container with port mapping to access the Gradio UI:

```bash
docker run -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  -e PYTHONUNBUFFERED=1 \
  qa-agent
```

Access the Gradio interface at `http://localhost:7860`.

### With Environment File

If you have a `.env` file, mount it:

```bash
docker run -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  --env-file .env \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  -e PYTHONUNBUFFERED=1 \
  qa-agent
```

### With Volume Mount (For Development)

Mount the `tests/generated` directory to edit files on your host and see changes in the container:

```bash
docker run -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  --env-file .env \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd)/tests/generated:/app/tests/generated" \
  qa-agent
```

## Manual Debugging & Healing Workflow

This workflow simulates a CI/CD environment locally to debug flaky tests, analyze failure reports, and run the self-healing agent manually.

### Step 1: Launch the Container with Volume Mount

Run the Docker container with a volume mount to enable file editing from your host machine:

```bash
docker run -d -p 7860:7860 \
  --add-host=host.docker.internal:host-gateway \
  --env-file .env \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1" \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd)/tests/generated:/app/tests/generated" \
  --name qa-agent-container \
  qa-agent
```

The `-d` flag runs the container in detached mode, and `--name` assigns a name for easier reference.

### Step 2: Access the Container Shell

Get a command-line interface inside the container:

1. **Find the Container ID or Name:**

   ```bash
   docker ps
   ```

2. **Open the Shell:**

   ```bash
   docker exec -it qa-agent-container /bin/bash
   ```

   Or use the container ID:

   ```bash
   docker exec -it <CONTAINER_ID> /bin/bash
   ```

You are now inside the container (`root@<container-id>:/app#`).

### Step 3: Run Tests Manually (CLI)

Execute Playwright tests directly from the command line to verify failures:

**Run All Tests:**

```bash
npx playwright test
```

**Run a Specific Test:**

```bash
npx playwright test tests/generated/broken_example.spec.ts
```

**Run with Verbose Output:**

```bash
npx playwright test --reporter=list
```

### Step 4: Extract Test Reports

Copy the Playwright HTML report from the container to your host machine:

**On your Host Machine (not inside Docker):**

```bash
# Syntax: docker cp <ContainerName>:<PathInside> <PathOnHost>
docker cp qa-agent-container:/app/playwright-report ./playwright-report
```

**View the Report:**

```bash
open playwright-report/index.html
```

### Step 5: Run the Self-Healing Agent (CLI)

If a test fails, invoke the Healer agent manually to fix the code:

**Inside the Docker Shell:**

```bash
python -m src.agents.healer tests/generated/broken_example.spec.ts
```

**Expected Workflow:**

1. **Runs Test:** Executes the test and captures failure output
2. **Analyzes:** Sends error logs and code to LLM for analysis
3. **Heals:** Overwrites the file with the fixed code
4. **Verifies:** Runs the test again to confirm it passes

> **Note:** With the volume mount, fixes applied inside the container immediately appear in the file on your local machine (VS Code).

## Container Management

### Stop the Container

```bash
docker stop qa-agent-container
```

### Start a Stopped Container

```bash
docker start qa-agent-container
```

### Remove the Container

```bash
docker rm qa-agent-container
```

### View Container Logs

```bash
docker logs qa-agent-container
```

### Follow Logs in Real-Time

```bash
docker logs -f qa-agent-container
```

## Troubleshooting

### LM Studio Connection Issues

If the container cannot reach LM Studio on your host:

1. Ensure LM Studio is running on port 1234
2. Use `host.docker.internal` to connect to your host machine
3. Check firewall settings if needed

### Permission Issues

If you encounter permission errors with mounted volumes, adjust file permissions as needed.

### Container Won't Start

Check logs for errors:

```bash
docker logs qa-agent-container
```

### Port Already in Use

If port 7860 is already in use, use a different port:

```bash
docker run -p 7861:7860 ...
```

## Environment Variables

Key environment variables for Docker:

- `LM_STUDIO_URL`: LM Studio API endpoint (default: `http://localhost:1234/v1`)
- `LM_STUDIO_API_KEY`: API key for LM Studio (default: `lm-studio`)
- `DEFAULT_MODEL`: Default model name (default: `local-model`)
- `VISION_MODEL`: Vision model name (default: `local-model`)
- `GRADIO_SERVER_NAME`: Set to `0.0.0.0` in Dockerfile for container access
- `PYTHONUNBUFFERED`: Set to `1` for real-time log output

See [ENV_VARIABLES.md](ENV_VARIABLES.md) for complete documentation.
