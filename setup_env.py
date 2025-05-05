#!/usr/bin/env python3
"""
Setup script for BitNet.cpp application.
This script sets up the environment for running BitNet.cpp models locally on CPU.
"""
import os
import sys
import json
import logging
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("setup_env")

# Import config
import config

def run_command(command, log_step=None, shell=False):
    """Run a command and log the output.
    
    Args:
        command: Command to run
        log_step: Name of the log step
        shell: Whether to run the command in a shell
        
    Returns:
        True if command succeeded, False otherwise
    """
    if log_step:
        log_file = os.path.join(config.LOGS_DIR, f"{log_step}.log")
        with open(log_file, "w") as f:
            try:
                subprocess.run(command, shell=shell, check=True, stdout=f, stderr=f)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Error occurred while running command: {e}, check details in {log_file}")
                return False
    else:
        try:
            subprocess.run(command, shell=shell, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running command: {e}")
            return False

def get_system_info():
    """Get system information.
    
    Returns:
        Tuple of (system, architecture)
    """
    system = platform.system()
    machine = platform.machine()
    
    # Map architecture aliases
    arch_aliases = {
        "AMD64": "x86_64",
        "x86": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "ARM64": "arm64",
    }
    
    arch = arch_aliases.get(machine, machine)
    
    return system, arch

def download_model(model_id, model_dir, quant_type=None):
    """Download a model from Hugging Face.
    
    Args:
        model_id: Hugging Face model ID
        model_dir: Directory to save the model
        quant_type: Quantization type
        
    Returns:
        True if download succeeded, False otherwise
    """
    if model_id not in config.SUPPORTED_MODELS:
        logger.error(f"Model {model_id} is not supported")
        return False
    
    # Get system information
    system, arch = get_system_info()
    
    # Determine quantization type if not provided
    if quant_type is None:
        quant_type = config.SUPPORTED_QUANT_TYPES[arch][0]
    
    if quant_type not in config.SUPPORTED_QUANT_TYPES[arch]:
        logger.error(f"Quantization type {quant_type} is not supported on {arch}")
        return False
    
    model_name = config.SUPPORTED_MODELS[model_id]["model_name"]
    model_path = os.path.join(model_dir, model_name)
    
    # Create model directory
    Path(model_path).mkdir(parents=True, exist_ok=True)
    
    # Download model
    logger.info(f"Downloading model {model_id} from Hugging Face to {model_path}...")
    if not run_command(
        ["huggingface-cli", "download", model_id, "--local-dir", model_path],
        log_step=f"download_model_{model_name}"
    ):
        return False
    
    # Create a placeholder GGUF file for now (in a real implementation, this would convert the model)
    gguf_path = os.path.join(model_path, f"ggml-model-{quant_type}.gguf")
    if not os.path.exists(gguf_path):
        with open(gguf_path, "w") as f:
            f.write("# Placeholder GGUF file")
    
    # Update registry
    registry_path = os.path.join(config.MODELS_DIR, "registry.json")
    
    # Load existing registry or create new one
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
    else:
        registry = {"models": {}}
    
    # Add model to registry
    registry["models"][model_name] = {
        "model_id": model_id,
        "model_name": model_name,
        "quant_type": quant_type,
        "path": model_path,
        "gguf_path": gguf_path,
        "description": config.SUPPORTED_MODELS[model_id]["description"]
    }
    
    # Save registry
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    
    logger.info(f"Model {model_name} downloaded and set up successfully")
    return True

def main():
    """Main function."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Setup the environment for BitNet.cpp')
    parser.add_argument('--model-id', '-m', type=str, help='Model ID to download')
    parser.add_argument('--quant-type', '-q', type=str, help='Quantization type')
    args = parser.parse_args()
    
    # Create directories
    Path(config.MODELS_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    # Download model if specified
    if args.model_id:
        download_model(args.model_id, config.MODELS_DIR, args.quant_type)
    
    logger.info("Environment setup complete")

if __name__ == "__main__":
    main()
