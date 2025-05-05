"""
Inference module for BitNet.cpp application.
Handles running inference on models locally on CPU.
"""
import os
import sys
import json
import logging
import platform
import subprocess
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable, Iterator

import config
from model_manager import ModelManager

class InferenceEngine:
    def __init__(self, model_manager: ModelManager):
        """Initialize the inference engine.

        Args:
            model_manager: Model manager instance
        """
        self.model_manager = model_manager

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(model_manager.logs_dir, "inference.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("inference")

        # Get system information
        self.system = platform.system()

    def _get_llama_cli_path(self) -> str:
        """Get the path to the llama-cli binary.

        For now, we'll use a mock implementation since we don't have the actual binary.
        In a real implementation, this would return the path to the compiled llama-cli binary.
        """
        # Check if we're in mock mode
        if os.environ.get("BITNET_MOCK_MODE", "1") == "1":
            # Return the path to our mock script
            mock_path = os.path.join(os.path.dirname(__file__), "mock_llama_cli.py")

            # Create the mock script if it doesn't exist
            if not os.path.exists(mock_path):
                with open(mock_path, "w") as f:
                    f.write('''#!/usr/bin/env python3
import sys
import time
import random

def main():
    """Mock implementation of llama-cli for testing."""
    # Parse arguments
    prompt = ""
    for i, arg in enumerate(sys.argv):
        if arg == "-p" and i + 1 < len(sys.argv):
            prompt = sys.argv[i + 1]

    # Print the prompt first
    print(prompt)

    # Generate some mock response
    responses = [
        "I'm a BitNet model running in mock mode. I can't provide real responses yet.",
        "This is a placeholder response from the mock llama-cli implementation.",
        "When the real BitNet.cpp integration is complete, you'll see actual model outputs here.",
        "For now, I'm just generating random text to simulate a response."
    ]

    # Print the response with some delay to simulate thinking
    time.sleep(1)
    for char in random.choice(responses):
        print(char, end="", flush=True)
        time.sleep(0.01)
    print()

if __name__ == "__main__":
    main()
''')

            return sys.executable + " " + mock_path

        # Real implementation would look for the actual binary
        build_dir = "build"
        if self.system == "Windows":
            main_path = os.path.join(build_dir, "bin", "Release", "llama-cli.exe")
            if not os.path.exists(main_path):
                main_path = os.path.join(build_dir, "bin", "llama-cli")
        else:
            main_path = os.path.join(build_dir, "bin", "llama-cli")

        if not os.path.exists(main_path):
            self.logger.warning(f"llama-cli binary not found at {main_path}, using mock implementation")
            return self._get_llama_cli_path()  # Recursively call to get mock path

        return main_path

    def run_inference(self,
                     model_name: str,
                     prompt: str,
                     n_predict: int = 128,
                     threads: int = 4,
                     ctx_size: int = 2048,
                     temperature: float = 0.8,
                     conversation: bool = False) -> str:
        """Run inference on a model using CPU only.

        This function runs the model entirely on the CPU, with no GPU acceleration.
        All processing is done locally on the machine.

        Args:
            model_name: Name of the model to use
            prompt: Prompt to generate text from
            n_predict: Number of tokens to predict
            threads: Number of threads to use
            ctx_size: Context size
            temperature: Temperature for sampling
            conversation: Whether to use conversation mode

        Returns:
            Generated text
        """
        model_path = self.model_manager.get_model_path(model_name)
        if model_path is None:
            raise ValueError(f"Model {model_name} not found")

        llama_cli = self._get_llama_cli_path()

        # Check if we're using the mock implementation
        if llama_cli.endswith("mock_llama_cli.py"):
            # For mock implementation, we need to handle the command differently
            command_str = f"{llama_cli} -m {model_path} -n {n_predict} -t {threads} -p \"{prompt}\" -ngl 0 -c {ctx_size} --temp {temperature} -b 1"
            if conversation:
                command_str += " -cnv"

            try:
                result = subprocess.run(command_str, shell=True, capture_output=True, text=True, check=True)
                return result.stdout
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error running inference with mock: {e}")
                self.logger.error(f"stderr: {e.stderr}")
                raise RuntimeError(f"Error running inference with mock: {e}")
        else:
            # For real implementation
            command = [
                llama_cli,
                '-m', model_path,
                '-n', str(n_predict),
                '-t', str(threads),
                '-p', prompt,
                '-ngl', '0',
                '-c', str(ctx_size),
                '--temp', str(temperature),
                "-b", "1",
            ]

            if conversation:
                command.append("-cnv")

            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return result.stdout
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error running inference: {e}")
                self.logger.error(f"stderr: {e.stderr}")
                raise RuntimeError(f"Error running inference: {e}")

    def stream_inference(self,
                        model_name: str,
                        prompt: str,
                        callback: Callable[[str], None],
                        n_predict: int = 128,
                        threads: int = 4,
                        ctx_size: int = 2048,
                        temperature: float = 0.8,
                        conversation: bool = False) -> None:
        """Stream inference results from a model.

        Args:
            model_name: Name of the model to use
            prompt: Prompt to generate text from
            callback: Callback function to call with each chunk of generated text
            n_predict: Number of tokens to predict
            threads: Number of threads to use
            ctx_size: Context size
            temperature: Temperature for sampling
            conversation: Whether to use conversation mode
        """
        model_path = self.model_manager.get_model_path(model_name)
        if model_path is None:
            raise ValueError(f"Model {model_name} not found")

        llama_cli = self._get_llama_cli_path()

        # Check if we're using the mock implementation
        if llama_cli.endswith("mock_llama_cli.py"):
            # For mock implementation, we need to handle the command differently
            command_str = f"{llama_cli} -m {model_path} -n {n_predict} -t {threads} -p \"{prompt}\" -ngl 0 -c {ctx_size} --temp {temperature} -b 1"
            if conversation:
                command_str += " -cnv"

            try:
                process = subprocess.Popen(
                    command_str,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                # Read stdout in a separate thread to avoid blocking
                def read_stdout():
                    for line in iter(process.stdout.readline, ''):
                        callback(line)

                stdout_thread = threading.Thread(target=read_stdout)
                stdout_thread.daemon = True
                stdout_thread.start()

                # Wait for process to complete
                process.wait()
                stdout_thread.join()

                if process.returncode != 0:
                    stderr = process.stderr.read()
                    self.logger.error(f"Error running inference with mock: {stderr}")
                    raise RuntimeError(f"Error running inference with mock: {stderr}")

            except Exception as e:
                self.logger.error(f"Error streaming inference with mock: {e}")
                raise RuntimeError(f"Error streaming inference with mock: {e}")
        else:
            # For real implementation
            command = [
                llama_cli,
                '-m', model_path,
                '-n', str(n_predict),
                '-t', str(threads),
                '-p', prompt,
                '-ngl', '0',
                '-c', str(ctx_size),
                '--temp', str(temperature),
                "-b", "1",
            ]

            if conversation:
                command.append("-cnv")

            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                # Read stdout in a separate thread to avoid blocking
                def read_stdout():
                    for line in iter(process.stdout.readline, ''):
                        callback(line)

                stdout_thread = threading.Thread(target=read_stdout)
                stdout_thread.daemon = True
                stdout_thread.start()

                # Wait for process to complete
                process.wait()
                stdout_thread.join()

                if process.returncode != 0:
                    stderr = process.stderr.read()
                    self.logger.error(f"Error running inference: {stderr}")
                    raise RuntimeError(f"Error running inference: {stderr}")

            except Exception as e:
                self.logger.error(f"Error streaming inference: {e}")
                raise RuntimeError(f"Error streaming inference: {e}")

    def chat_completion(self,
                       model_name: str,
                       messages: List[Dict[str, str]],
                       n_predict: int = 128,
                       threads: int = 4,
                       ctx_size: int = 2048,
                       temperature: float = 0.8) -> Dict[str, Any]:
        """Generate a chat completion.

        Args:
            model_name: Name of the model to use
            messages: List of messages in the conversation
            n_predict: Number of tokens to predict
            threads: Number of threads to use
            ctx_size: Context size
            temperature: Temperature for sampling

        Returns:
            Dictionary with completion information
        """
        # Format messages into a prompt
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        # Add final assistant prompt
        prompt += "Assistant: "

        # Run inference
        response = self.run_inference(
            model_name=model_name,
            prompt=prompt,
            n_predict=n_predict,
            threads=threads,
            ctx_size=ctx_size,
            temperature=temperature,
            conversation=True
        )

        # Extract assistant response
        assistant_response = response.split("Assistant: ")[-1].strip()

        return {
            "id": "chat-" + model_name,
            "object": "chat.completion",
            "created": int(import_time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": assistant_response
                    },
                    "finish_reason": "stop"
                }
            ]
        }

    def stream_chat_completion(self,
                              model_name: str,
                              messages: List[Dict[str, str]],
                              callback: Callable[[Dict[str, Any]], None],
                              n_predict: int = 128,
                              threads: int = 4,
                              ctx_size: int = 2048,
                              temperature: float = 0.8) -> None:
        """Stream a chat completion.

        Args:
            model_name: Name of the model to use
            messages: List of messages in the conversation
            callback: Callback function to call with each chunk of generated text
            n_predict: Number of tokens to predict
            threads: Number of threads to use
            ctx_size: Context size
            temperature: Temperature for sampling
        """
        # Format messages into a prompt
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        # Add final assistant prompt
        prompt += "Assistant: "

        # Buffer for collecting response
        response_buffer = ""

        # Callback for streaming
        def stream_callback(chunk: str):
            nonlocal response_buffer
            response_buffer += chunk

            # Extract assistant response
            if "Assistant: " in response_buffer:
                assistant_response = response_buffer.split("Assistant: ")[-1].strip()

                # Create response object
                response = {
                    "id": "chat-" + model_name,
                    "object": "chat.completion.chunk",
                    "created": int(import_time()),
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": chunk
                            },
                            "finish_reason": None
                        }
                    ]
                }

                callback(response)

        # Run streaming inference
        self.stream_inference(
            model_name=model_name,
            prompt=prompt,
            callback=stream_callback,
            n_predict=n_predict,
            threads=threads,
            ctx_size=ctx_size,
            temperature=temperature,
            conversation=True
        )

        # Send final chunk with finish_reason
        final_response = {
            "id": "chat-" + model_name,
            "object": "chat.completion.chunk",
            "created": int(import_time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }

        callback(final_response)

# Helper function to get current time
def import_time():
    import time
    return time.time()
