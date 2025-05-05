"""
Model manager for BitNet.cpp application.
Handles downloading, setting up, and managing models for local CPU-only inference.
All models are stored and run locally on your machine without requiring any cloud services.
"""
import os
import sys
import json
import logging
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import config

class ModelManager:
    def __init__(self, models_dir: str = config.MODELS_DIR, logs_dir: str = config.LOGS_DIR):
        """Initialize the model manager.

        Args:
            models_dir: Directory for storing models
            logs_dir: Directory for logs
        """
        self.models_dir = models_dir
        self.logs_dir = logs_dir

        # Create directories if they don't exist
        Path(self.models_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)

        # Initialize model registry
        self.registry_path = os.path.join(self.models_dir, "registry.json")
        self.registry = self._load_registry()

        # Get system information
        self.system, self.arch = self._get_system_info()

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, "model_manager.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("model_manager")

    def _get_system_info(self) -> Tuple[str, str]:
        """Get system and architecture information."""
        system = platform.system()
        machine = platform.machine()
        arch = config.ARCH_ALIAS.get(machine, machine)
        return system, arch

    def _load_registry(self) -> Dict[str, Any]:
        """Load the model registry from disk."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"models": {}}
        return {"models": {}}

    def _save_registry(self) -> None:
        """Save the model registry to disk."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def _run_command(self, command: List[str], shell: bool = False, log_step: Optional[str] = None) -> bool:
        """Run a system command and ensure it succeeds.

        Args:
            command: Command to run
            shell: Whether to run in shell
            log_step: Name of log step for logging output

        Returns:
            True if command succeeded, False otherwise
        """
        if log_step:
            log_file = os.path.join(self.logs_dir, f"{log_step}.log")
            with open(log_file, "w") as f:
                try:
                    subprocess.run(command, shell=shell, check=True, stdout=f, stderr=f)
                    return True
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Error occurred while running command: {e}, check details in {log_file}")
                    return False
        else:
            try:
                subprocess.run(command, shell=shell, check=True)
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error occurred while running command: {e}")
                return False

    def list_available_models(self) -> Dict[str, Dict[str, str]]:
        """List all available models from Hugging Face."""
        return config.SUPPORTED_MODELS

    def list_installed_models(self) -> Dict[str, Dict[str, Any]]:
        """List all installed models."""
        return self.registry["models"]

    def download_model(self, model_id: str, quant_type: Optional[str] = None) -> bool:
        """Download a model from Hugging Face.

        Args:
            model_id: Hugging Face model ID
            quant_type: Quantization type (i2_s, tl1, tl2)

        Returns:
            True if download succeeded, False otherwise
        """
        if model_id not in config.SUPPORTED_MODELS:
            self.logger.error(f"Model {model_id} is not supported")
            return False

        # Determine quantization type if not provided
        if quant_type is None:
            quant_type = config.SUPPORTED_QUANT_TYPES[self.arch][0]

        if quant_type not in config.SUPPORTED_QUANT_TYPES[self.arch]:
            self.logger.error(f"Quantization type {quant_type} is not supported on {self.arch}")
            return False

        model_name = config.SUPPORTED_MODELS[model_id]["model_name"]
        model_dir = os.path.join(self.models_dir, model_name)

        # Create model directory
        Path(model_dir).mkdir(parents=True, exist_ok=True)

        # Download model
        self.logger.info(f"Downloading model {model_id} from Hugging Face to {model_dir}...")
        try:
            if not self._run_command(
                ["huggingface-cli", "download", model_id, "--local-dir", model_dir],
                log_step=f"download_model_{model_name}"
            ):
                return False
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return False

        # Create a placeholder GGUF file for now
        # In a real implementation, this would convert the model to GGUF format
        gguf_path = os.path.join(model_dir, f"ggml-model-{quant_type}.gguf")
        if not os.path.exists(gguf_path):
            with open(gguf_path, "w") as f:
                f.write("# Placeholder GGUF file")
            self.logger.info(f"Created placeholder GGUF file at {gguf_path}")

        # Update registry
        self.registry["models"][model_name] = {
            "model_id": model_id,
            "model_name": model_name,
            "quant_type": quant_type,
            "path": model_dir,
            "gguf_path": gguf_path,
            "description": config.SUPPORTED_MODELS[model_id]["description"]
        }
        self._save_registry()

        self.logger.info(f"Model {model_name} downloaded and set up successfully")
        return True

    def remove_model(self, model_name: str) -> bool:
        """Remove a model.

        Args:
            model_name: Name of the model to remove

        Returns:
            True if removal succeeded, False otherwise
        """
        if model_name not in self.registry["models"]:
            self.logger.error(f"Model {model_name} is not installed")
            return False

        model_dir = self.registry["models"][model_name]["path"]

        # Remove model directory
        try:
            shutil.rmtree(model_dir)
        except Exception as e:
            self.logger.error(f"Error removing model directory: {e}")
            return False

        # Update registry
        del self.registry["models"][model_name]
        self._save_registry()

        self.logger.info(f"Model {model_name} removed successfully")
        return True

    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get the path to a model's GGUF file.

        Args:
            model_name: Name of the model

        Returns:
            Path to the model's GGUF file, or None if not found
        """
        if model_name not in self.registry["models"]:
            return None

        return self.registry["models"][model_name]["gguf_path"]

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information, or None if not found
        """
        if model_name not in self.registry["models"]:
            return None

        return self.registry["models"][model_name]
