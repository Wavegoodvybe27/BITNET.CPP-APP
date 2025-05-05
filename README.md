# BitNet.cpp App

A desktop application for downloading, managing, and running BitNet models locally on CPU, similar to Ollama but specifically for BitNet.cpp models. This application runs entirely locally and performs all inference on your CPU without requiring any cloud services or GPU acceleration.

## Features

- Download and manage BitNet models from Hugging Face
- Run inference on models locally on your CPU via API, CLI, or desktop UI
- Chat with models through a web UI or desktop application with all processing done locally
- Stream responses for a better user experience
- Support for different quantization types (i2_s, tl1, tl2)
- 100% local execution with no data sent to external services

## Prerequisites

- Python 3.9 or higher
- CMake
- C++ compiler (Clang recommended)
- Git

## Installation

1. Clone the repository with submodules:
   ```bash
   git clone --recursive https://github.com/microsoft/BitNet.git
   cd BitNet
   ```

2. Install the dependencies:
   ```bash
   # (Recommended) Create a new conda environment
   conda create -n bitnet-app python=3.9
   conda activate bitnet-app

   # Install requirements for CLI and API
   pip install -r requirements.txt

   # For desktop UI, install additional requirements
   pip install -r requirements_desktop.txt
   ```

3. Build the BitNet.cpp framework:
   ```bash
   python setup_env.py
   ```

## Usage

### Opening the Project in VSCode

For the best development experience with automatic environment activation:

```bash
# On Windows
open_bitnet_project.bat

# On Linux/macOS
chmod +x open_project.sh
./open_project.sh
```

This will:
1. Open VSCode with the BitNet.cpp workspace
2. Automatically activate the virtual environment
3. Set up the correct Python interpreter
4. Configure the integrated terminal to use the environment

When you close VSCode, the environment will be automatically deactivated.

### Using the Desktop UI

Start the desktop application:

```bash
# On Windows
bitnet-desktop.bat

# Or directly with Python
python bitnet_desktop.py
```

This will launch the desktop application with a graphical user interface for managing models, running inference, and chatting with models. The application also starts the API server in the background, so you can still use the web UI if preferred.

### Starting the Server (without Desktop UI)

If you prefer to use only the web UI without the desktop application, you can start just the API server:

```bash
python bitnet_cli.py server start
```

This will start the server at http://127.0.0.1:8000. You can access the web UI by opening this URL in your browser.

### Using the CLI

The CLI provides simple commands similar to Ollama for managing models and running inference:

```bash
# On Windows
bitnet list                                # List all models
bitnet pull microsoft/BitNet-b1.58-2B-4T   # Download a model
bitnet rm BitNet-b1.58-2B-4T               # Remove a model
bitnet run BitNet-b1.58-2B-4T -p "Hello, world!"  # Run inference
bitnet chat BitNet-b1.58-2B-4T             # Start a chat session
bitnet serve                               # Start the server

# On Linux/macOS (make the script executable first with: chmod +x bitnet.sh)
./bitnet.sh list
./bitnet.sh pull microsoft/BitNet-b1.58-2B-4T
```

#### Additional Options

```bash
# Run with system prompt
bitnet run BitNet-b1.58-2B-4T -s "You are a helpful assistant" -p "Tell me about quantum computing"

# Chat with system prompt
bitnet chat BitNet-b1.58-2B-4T -s "You are a helpful assistant"

# Adjust generation parameters
bitnet run BitNet-b1.58-2B-4T -p "Write a poem" --tokens 256 --temp 0.9 --threads 8
```

### Using the API

The API provides endpoints for managing models and running inference:

```bash
# List available models
GET /models/available

# List installed models
GET /models/installed

# Download a model
POST /models/download
{
  "model_id": "microsoft/BitNet-b1.58-2B-4T",
  "quant_type": "i2_s"
}

# Remove a model
DELETE /models/{model_name}

# Get model info
GET /models/{model_name}

# Run inference
POST /inference
{
  "model": "BitNet-b1.58-2B-4T",
  "prompt": "Hello, world!",
  "n_predict": 128,
  "threads": 4,
  "ctx_size": 2048,
  "temperature": 0.8,
  "conversation": false
}

# Stream inference
POST /inference/stream
{
  "model": "BitNet-b1.58-2B-4T",
  "prompt": "Hello, world!",
  "n_predict": 128,
  "threads": 4,
  "ctx_size": 2048,
  "temperature": 0.8,
  "conversation": false
}

# Chat completion
POST /chat/completions
{
  "model": "BitNet-b1.58-2B-4T",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ],
  "n_predict": 128,
  "threads": 4,
  "ctx_size": 2048,
  "temperature": 0.8,
  "stream": false
}
```

## Supported Models

The following BitNet models are supported:

- microsoft/BitNet-b1.58-2B-4T
- 1bitLLM/bitnet_b1_58-large
- 1bitLLM/bitnet_b1_58-3B
- HF1BitLLM/Llama3-8B-1.58-100B-tokens
- tiiuae/Falcon3-1B-Instruct-1.58bit
- tiiuae/Falcon3-3B-Instruct-1.58bit
- tiiuae/Falcon3-7B-Instruct-1.58bit
- tiiuae/Falcon3-10B-Instruct-1.58bit

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [BitNet.cpp](https://github.com/microsoft/BitNet) - The official inference framework for 1-bit LLMs
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - The base framework for BitNet.cpp
- [Ollama](https://github.com/ollama/ollama) - Inspiration for this application
