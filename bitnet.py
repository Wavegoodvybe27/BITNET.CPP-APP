#!/usr/bin/env python3
"""
Simplified command-line interface for BitNet.cpp application.
All processing is done locally on your machine without requiring any cloud services or GPU.
"""
import os
import sys
import json
import argparse
import platform
import requests
import subprocess
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
        """Create argument parser with simplified commands."""
        parser = argparse.ArgumentParser(description="BitNet.cpp CLI")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # List command
        list_parser = subparsers.add_parser("list", help="List models")
        
        # Pull command (download)
        pull_parser = subparsers.add_parser("pull", help="Download a model")
        pull_parser.add_argument("model_id", type=str, help="Model ID to download")
        pull_parser.add_argument("--quant", type=str, help="Quantization type (i2_s, tl1, tl2)")
        
        # Remove command
        rm_parser = subparsers.add_parser("rm", help="Remove a model")
        rm_parser.add_argument("model_name", type=str, help="Model name to remove")
        
        # Run command
        run_parser = subparsers.add_parser("run", help="Run a model")
        run_parser.add_argument("model", type=str, help="Model to use")
        run_parser.add_argument("--prompt", "-p", type=str, help="Prompt to generate text from")
        run_parser.add_argument("--system", "-s", type=str, help="System message for chat")
        run_parser.add_argument("--tokens", "-n", type=int, default=128, help="Number of tokens to predict")
        run_parser.add_argument("--threads", "-t", type=int, default=4, help="Number of threads to use")
        run_parser.add_argument("--ctx", "-c", type=int, default=2048, help="Context size")
        run_parser.add_argument("--temp", type=float, default=0.8, help="Temperature for sampling")
        
        # Chat command
        chat_parser = subparsers.add_parser("chat", help="Start a chat session")
        chat_parser.add_argument("model", type=str, help="Model to use")
        chat_parser.add_argument("--system", "-s", type=str, help="System message")
        chat_parser.add_argument("--tokens", "-n", type=int, default=128, help="Number of tokens to predict")
        chat_parser.add_argument("--threads", "-t", type=int, default=4, help="Number of threads to use")
        chat_parser.add_argument("--ctx", "-c", type=int, default=2048, help="Context size")
        chat_parser.add_argument("--temp", type=float, default=0.8, help="Temperature for sampling")
        
        # Serve command
        serve_parser = subparsers.add_parser("serve", help="Start the server")
        serve_parser.add_argument("--host", type=str, default=config.API_HOST, help="Host to bind to")
        serve_parser.add_argument("--port", type=int, default=config.API_PORT, help="Port to bind to")
        
        return parser
    
    def _run_command(self) -> None:
        """Run the specified command."""
        if self.args.command is None:
            self.parser.print_help()
            return
        
        # List command
        if self.args.command == "list":
            self._list_models()
        
        # Pull command
        elif self.args.command == "pull":
            self._pull_model()
        
        # Remove command
        elif self.args.command == "rm":
            self._remove_model()
        
        # Run command
        elif self.args.command == "run":
            self._run_model()
        
        # Chat command
        elif self.args.command == "chat":
            self._chat_with_model()
        
        # Serve command
        elif self.args.command == "serve":
            self._start_server()
    
    def _list_models(self) -> None:
        """List available and installed models."""
        try:
            # Try to use API
            response = requests.get(f"{self.api_url}/models/installed")
            installed_models = response.json()
        except:
            # Fall back to local model manager
            installed_models = self.model_manager.list_installed_models()
        
        if installed_models:
            print("Installed models:")
            for model_name, info in installed_models.items():
                print(f"  {model_name} - {info['description']}")
        else:
            print("No models installed. Use 'bitnet pull <model_id>' to download a model.")
            
            try:
                # Try to use API
                response = requests.get(f"{self.api_url}/models/available")
                available_models = response.json()
            except:
                # Fall back to local model manager
                available_models = self.model_manager.list_available_models()
            
            print("\nAvailable models to pull:")
            for model_id, info in available_models.items():
                print(f"  {model_id} - {info['description']}")
    
    def _pull_model(self) -> None:
        """Download a model."""
        model_id = self.args.model_id
        quant_type = self.args.quant
        
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
    
    def _run_model(self) -> None:
        """Run inference with a model."""
        model = self.args.model
        prompt = self.args.prompt
        system = self.args.system
        
        if not prompt and not system:
            print("Error: Either --prompt or --system must be provided")
            return
        
        # If system is provided but no prompt, start a chat session
        if system and not prompt:
            self._chat_with_model()
            return
        
        # If prompt is provided, run inference
        n_predict = self.args.tokens
        threads = self.args.threads
        ctx_size = self.args.ctx
        temperature = self.args.temp
        
        # Prepend system message if provided
        if system:
            full_prompt = f"System: {system}\n\nUser: {prompt}\n\nAssistant: "
            conversation = True
        else:
            full_prompt = prompt
            conversation = False
        
        try:
            # Try to use API
            response = requests.post(
                f"{self.api_url}/inference",
                json={
                    "model": model,
                    "prompt": full_prompt,
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
            try:
                response = self.inference_engine.run_inference(
                    model_name=model,
                    prompt=full_prompt,
                    n_predict=n_predict,
                    threads=threads,
                    ctx_size=ctx_size,
                    temperature=temperature,
                    conversation=conversation
                )
                print(response)
            except Exception as e:
                print(f"Error running inference: {e}")
    
    def _chat_with_model(self) -> None:
        """Start a chat session with a model."""
        model = self.args.model
        system = self.args.system
        n_predict = self.args.tokens
        threads = self.args.threads
        ctx_size = self.args.ctx
        temperature = self.args.temp
        
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
    
    def _start_server(self) -> None:
        """Start the server."""
        print(f"Starting server on {self.args.host}:{self.args.port}...")
        
        try:
            # Import here to avoid circular imports
            import uvicorn
            from server import app
            
            uvicorn.run(
                app,
                host=self.args.host,
                port=self.args.port
            )
        except ImportError:
            # If uvicorn is not installed, use subprocess
            subprocess.run([
                sys.executable,
                "server.py"
            ])

if __name__ == "__main__":
    BitNetCLI()
