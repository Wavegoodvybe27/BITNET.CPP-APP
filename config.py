"""
Configuration settings for the BitNet.cpp application.
This application runs entirely locally and performs all inference on CPU.
No cloud services or GPU acceleration is required.
"""
import os
from pathlib import Path

# Base directory for the application
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Directory for storing models
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Directory for logs
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Default model settings
DEFAULT_MODEL = "microsoft/BitNet-b1.58-2B-4T"

# API server settings
API_HOST = "127.0.0.1"
API_PORT = 8000

# Supported quantization types by architecture
SUPPORTED_QUANT_TYPES = {
    "arm64": ["i2_s", "tl1"],
    "x86_64": ["i2_s", "tl2"]
}

# Supported models from Hugging Face
SUPPORTED_MODELS = {
    "microsoft/BitNet-b1.58-2B-4T": {
        "model_name": "BitNet-b1.58-2B-4T",
        "description": "Official BitNet 2B parameter model (4T tokens)"
    },
    "1bitLLM/bitnet_b1_58-large": {
        "model_name": "bitnet_b1_58-large",
        "description": "BitNet b1.58 large model"
    },
    "1bitLLM/bitnet_b1_58-3B": {
        "model_name": "bitnet_b1_58-3B",
        "description": "BitNet b1.58 3B model"
    },
    "HF1BitLLM/Llama3-8B-1.58-100B-tokens": {
        "model_name": "Llama3-8B-1.58-100B-tokens",
        "description": "Llama3 8B model quantized to 1.58 bits (100B tokens)"
    },
    "tiiuae/Falcon3-1B-Instruct-1.58bit": {
        "model_name": "Falcon3-1B-Instruct-1.58bit",
        "description": "Falcon3 1B Instruct model quantized to 1.58 bits"
    },
    "tiiuae/Falcon3-3B-Instruct-1.58bit": {
        "model_name": "Falcon3-3B-Instruct-1.58bit",
        "description": "Falcon3 3B Instruct model quantized to 1.58 bits"
    },
    "tiiuae/Falcon3-7B-Instruct-1.58bit": {
        "model_name": "Falcon3-7B-Instruct-1.58bit",
        "description": "Falcon3 7B Instruct model quantized to 1.58 bits"
    },
    "tiiuae/Falcon3-10B-Instruct-1.58bit": {
        "model_name": "Falcon3-10B-Instruct-1.58bit",
        "description": "Falcon3 10B Instruct model quantized to 1.58 bits"
    }
}

# Architecture-specific compiler arguments
COMPILER_EXTRA_ARGS = {
    "arm64": ["-DBITNET_ARM_TL1=ON"],
    "x86_64": ["-DBITNET_X86_TL2=ON"]
}

# OS-specific compiler arguments
OS_EXTRA_ARGS = {
    "Windows": ["-T", "ClangCL"],
}

# Architecture aliases
ARCH_ALIAS = {
    "AMD64": "x86_64",
    "x86": "x86_64",
    "x86_64": "x86_64",
    "aarch64": "arm64",
    "arm64": "arm64",
    "ARM64": "arm64",
}
