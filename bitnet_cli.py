#!/usr/bin/env python3
"""
Command-line interface for BitNet.cpp application.
Provides commands for model management and local CPU-only inference.
All processing is done locally on your machine without requiring any cloud services or GPU.
"""
import os
import sys
import json
import argparse
import platform
import requests
from typing import Dict, List, Optional, Any

import config
from model_manager import ModelManager
from inference import InferenceEngine

class BitNetCLI:
    def __init__(self):
        """Initialize the CLI."""
        self.model_manager = ModelManager()
        self.inference_engine = InferenceEngine(self.model_manager)

        # Set up API client
        self.api_url = f"http://{config.API_HOST}:{config.API_PORT}"

        # Parse arguments
        self.parser = self._create_parser()
        self.args = self.parser.parse_args()

        # Run command
        self._run_command()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(description="BitNet.cpp CLI")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # Server commands
        server_parser = subparsers.add_parser("server", help="Server commands")
        server_subparsers = server_parser.add_subparsers(dest="server_command", help="Server command to run")

        # Start server
        start_parser = server_subparsers.add_parser("start", help="Start the server")
        start_parser.add_argument("--host", type=str, default=config.API_HOST, help="Host to bind to")
        start_parser.add_argument("--port", type=int, default=config.API_PORT, help="Port to bind to")

        # Model commands
        model_parser = subparsers.add_parser("model", help="Model commands")
        model_subparsers = model_parser.add_subparsers(dest="model_command", help="Model command to run")

        # List available models
        model_subparsers.add_parser("list-available", help="List available models")

        # List installed models
        model_subparsers.add_parser("list-installed", help="List installed models")

        # Download model
        download_parser = model_subparsers.add_parser("download", help="Download a model")
        download_parser.add_argument("model_id", type=str, help="Model ID to download")
        download_parser.add_argument("--quant-type", type=str, help="Quantization type")

        # Remove model
        remove_parser = model_subparsers.add_parser("remove", help="Remove a model")
        remove_parser.add_argument("model_name", type=str, help="Model name to remove")

        # Show model info
        info_parser = model_subparsers.add_parser("info", help="Show model info")
        info_parser.add_argument("model_name", type=str, help="Model name to show info for")

        # Run commands
        run_parser = subparsers.add_parser("run", help="Run commands")
        run_subparsers = run_parser.add_subparsers(dest="run_command", help="Run command to run")

        # Run inference
        inference_parser = run_subparsers.add_parser("inference", help="Run inference")
        inference_parser.add_argument("model", type=str, help="Model to use")
        inference_parser.add_argument("--prompt", "-p", type=str, required=True, help="Prompt to generate text from")
        inference_parser.add_argument("--n-predict", "-n", type=int, default=128, help="Number of tokens to predict")
        inference_parser.add_argument("--threads", "-t", type=int, default=4, help="Number of threads to use")
        inference_parser.add_argument("--ctx-size", "-c", type=int, default=2048, help="Context size")
        inference_parser.add_argument("--temperature", "--temp", type=float, default=0.8, help="Temperature for sampling")
        inference_parser.add_argument("--conversation", "-cnv", action="store_true", help="Use conversation mode")

        # Run chat
        chat_parser = run_subparsers.add_parser("chat", help="Run chat")
        chat_parser.add_argument("model", type=str, help="Model to use")
        chat_parser.add_argument("--system", "-s", type=str, help="System message")
        chat_parser.add_argument("--n-predict", "-n", type=int, default=128, help="Number of tokens to predict")
        chat_parser.add_argument("--threads", "-t", type=int, default=4, help="Number of threads to use")
        chat_parser.add_argument("--ctx-size", "-c", type=int, default=2048, help="Context size")
        chat_parser.add_argument("--temperature", "--temp", type=float, default=0.8, help="Temperature for sampling")

        return parser

    def _run_command(self) -> None:
        """Run the specified command."""
        if self.args.command is None:
            self.parser.print_help()
            return

        # Server commands
        if self.args.command == "server":
            if self.args.server_command == "start":
                self._start_server()
            else:
                self.parser.print_help()

        # Model commands
        elif self.args.command == "model":
            if self.args.model_command == "list-available":
                self._list_available_models()
            elif self.args.model_command == "list-installed":
                self._list_installed_models()
            elif self.args.model_command == "download":
                self._download_model()
            elif self.args.model_command == "remove":
                self._remove_model()
            elif self.args.model_command == "info":
                self._show_model_info()
            else:
                self.parser.print_help()

        # Run commands
        elif self.args.command == "run":
            if self.args.run_command == "inference":
                self._run_inference()
            elif self.args.run_command == "chat":
                self._run_chat()
            else:
                self.parser.print_help()

    def _start_server(self) -> None:
        """Start the server."""
        print(f"Starting server on {self.args.host}:{self.args.port}...")

        # Import here to avoid circular imports
        import uvicorn
        from server import app

        uvicorn.run(
            app,
            host=self.args.host,
            port=self.args.port
        )

    def _list_available_models(self) -> None:
        """List available models."""
        try:
            # Try to use API
            response = requests.get(f"{self.api_url}/models/available")
            models = response.json()
        except:
            # Fall back to local model manager
            models = self.model_manager.list_available_models()

        print("Available models:")
        for model_id, info in models.items():
            print(f"  {model_id} - {info['description']}")

    def _list_installed_models(self) -> None:
        """List installed models."""
        try:
            # Try to use API
            response = requests.get(f"{self.api_url}/models/installed")
            models = response.json()
        except:
            # Fall back to local model manager
            models = self.model_manager.list_installed_models()

        print("Installed models:")
        for model_name, info in models.items():
            print(f"  {model_name} - {info['description']}")

    def _download_model(self) -> None:
        """Download a model."""
        model_id = self.args.model_id
        quant_type = self.args.quant_type

        try:
            # Try to use API
            response = requests.post(
                f"{self.api_url}/models/download",
                json={"model_id": model_id, "quant_type": quant_type}
            )
            print(response.json()["message"])
        except:
            # Fall back to local model manager
            print(f"Downloading model {model_id}...")
            success = self.model_manager.download_model(model_id, quant_type)
            if success:
                print(f"Model {model_id} downloaded successfully")
            else:
                print(f"Failed to download model {model_id}")

    def _remove_model(self) -> None:
        """Remove a model."""
        model_name = self.args.model_name

        try:
            # Try to use API
            response = requests.delete(f"{self.api_url}/models/{model_name}")
            print(response.json()["message"])
        except:
            # Fall back to local model manager
            print(f"Removing model {model_name}...")
            success = self.model_manager.remove_model(model_name)
            if success:
                print(f"Model {model_name} removed successfully")
            else:
                print(f"Failed to remove model {model_name}")

    def _show_model_info(self) -> None:
        """Show model info."""
        model_name = self.args.model_name

        try:
            # Try to use API
            response = requests.get(f"{self.api_url}/models/{model_name}")
            info = response.json()
        except:
            # Fall back to local model manager
            info = self.model_manager.get_model_info(model_name)
            if info is None:
                print(f"Model {model_name} not found")
                return

        print(f"Model: {model_name}")
        print(f"  ID: {info['model_id']}")
        print(f"  Quantization: {info['quant_type']}")
        print(f"  Path: {info['path']}")
        print(f"  GGUF Path: {info['gguf_path']}")
        print(f"  Description: {info['description']}")

    def _run_inference(self) -> None:
        """Run inference."""
        model = self.args.model
        prompt = self.args.prompt
        n_predict = self.args.n_predict
        threads = self.args.threads
        ctx_size = self.args.ctx_size
        temperature = self.args.temperature
        conversation = self.args.conversation

        try:
            # Try to use API
            response = requests.post(
                f"{self.api_url}/inference",
                json={
                    "model": model,
                    "prompt": prompt,
                    "n_predict": n_predict,
                    "threads": threads,
                    "ctx_size": ctx_size,
                    "temperature": temperature,
                    "conversation": conversation
                }
            )
            print(response.json()["response"])
        except:
            # Fall back to local inference engine
            print(f"Running inference with model {model}...")
            try:
                response = self.inference_engine.run_inference(
                    model_name=model,
                    prompt=prompt,
                    n_predict=n_predict,
                    threads=threads,
                    ctx_size=ctx_size,
                    temperature=temperature,
                    conversation=conversation
                )
                print(response)
            except Exception as e:
                print(f"Error running inference: {e}")

    def _run_chat(self) -> None:
        """Run chat."""
        model = self.args.model
        system = self.args.system
        n_predict = self.args.n_predict
        threads = self.args.threads
        ctx_size = self.args.ctx_size
        temperature = self.args.temperature

        # Create messages list
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        print(f"Chat with {model} (type 'exit' to quit)")

        while True:
            # Get user input
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break

            # Add user message
            messages.append({"role": "user", "content": user_input})

            try:
                # Try to use API
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "n_predict": n_predict,
                        "threads": threads,
                        "ctx_size": ctx_size,
                        "temperature": temperature,
                        "stream": False
                    }
                )
                assistant_response = response.json()["choices"][0]["message"]["content"]
            except:
                # Fall back to local inference engine
                try:
                    response = self.inference_engine.chat_completion(
                        model_name=model,
                        messages=messages,
                        n_predict=n_predict,
                        threads=threads,
                        ctx_size=ctx_size,
                        temperature=temperature
                    )
                    assistant_response = response["choices"][0]["message"]["content"]
                except Exception as e:
                    print(f"Error running chat: {e}")
                    continue

            # Print assistant response
            print(f"Assistant: {assistant_response}")

            # Add assistant message
            messages.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    BitNetCLI()
