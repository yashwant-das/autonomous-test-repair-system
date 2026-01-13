# Environment Variables

This document describes all environment variables used by the LM Studio QA Agent.

## Configuration

Create a `.env` file in the project root with the following variables:

```bash
# LM Studio Configuration
# URL where LM Studio is running (default: http://localhost:1234/v1)
LM_STUDIO_URL=http://localhost:1234/v1

# API Key for LM Studio (default: lm-studio)
LM_STUDIO_API_KEY=lm-studio

# Default model name for text generation (default: local-model)
DEFAULT_MODEL=local-model

# Vision model name for image analysis (default: local-model)
VISION_MODEL=local-model
```

## Variable Descriptions

### `LM_STUDIO_URL`

- **Type**: String (URL)
- **Default**: `http://localhost:1234/v1`
- **Description**: The base URL where LM Studio is running. This should point to the v1 API endpoint.

### `LM_STUDIO_API_KEY`

- **Type**: String
- **Default**: `lm-studio`
- **Description**: API key for authenticating with LM Studio. The default value works for local LM Studio instances.

### `DEFAULT_MODEL`

- **Type**: String
- **Default**: `local-model`
- **Description**: The name of the model to use for text generation (test generation and healing). This should match a
  model loaded in LM Studio.

### `VISION_MODEL`

- **Type**: String
- **Default**: `local-model`
- **Description**: The name of the vision-capable model to use for image analysis. This should match a vision model
  loaded in LM Studio (e.g., `qwen3-vl-30b`).

## Usage

The application uses `python-dotenv` to load these variables from a `.env` file. If no `.env` file exists, the defaults
listed above will be used.

## Example `.env` File

```bash
LM_STUDIO_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio
DEFAULT_MODEL=qwen3-coder-30b
VISION_MODEL=qwen3-vl-30b
```
