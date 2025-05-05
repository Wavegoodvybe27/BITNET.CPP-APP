#!/usr/bin/env python3
"""
Mock implementation of llama-cli for testing BitNet.cpp application.
This script simulates the behavior of the llama-cli binary for development and testing.
"""
import sys
import time
import random
import argparse

def main():
    """Mock implementation of llama-cli for testing."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Mock llama-cli for BitNet.cpp")
    parser.add_argument("-m", "--model", type=str, help="Model path")
    parser.add_argument("-n", "--n-predict", type=int, default=128, help="Number of tokens to predict")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("-p", "--prompt", type=str, default="", help="Prompt")
    parser.add_argument("-ngl", "--n-gpu-layers", type=int, default=0, help="Number of GPU layers")
    parser.add_argument("-c", "--ctx-size", type=int, default=2048, help="Context size")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature")
    parser.add_argument("-b", "--batch-size", type=int, default=1, help="Batch size")
    parser.add_argument("-cnv", "--conversation", action="store_true", help="Conversation mode")
    
    # Parse args or use sys.argv directly if parsing fails
    try:
        args = parser.parse_args()
        prompt = args.prompt
        conversation = args.conversation
    except:
        # Fallback to manual parsing
        prompt = ""
        conversation = False
        for i, arg in enumerate(sys.argv):
            if arg == "-p" and i + 1 < len(sys.argv):
                prompt = sys.argv[i + 1]
            if arg == "-cnv":
                conversation = True
    
    # Print the prompt first (this simulates how llama-cli would echo the prompt)
    print(prompt)
    
    # Generate some mock response
    responses = [
        "I'm a BitNet model running in mock mode. I can't provide real responses yet.",
        "This is a placeholder response from the mock llama-cli implementation.",
        "When the real BitNet.cpp integration is complete, you'll see actual model outputs here.",
        "For now, I'm just generating random text to simulate a response."
    ]
    
    # Add conversation-specific responses
    if conversation:
        responses.extend([
            "In conversation mode, I would maintain context between messages.",
            "The real BitNet models will be able to have coherent conversations.",
            "This is just a simulation of the conversation mode."
        ])
    
    # Print the response with some delay to simulate thinking
    time.sleep(1)
    response = random.choice(responses)
    
    # Stream the response character by character
    for char in response:
        print(char, end="", flush=True)
        time.sleep(0.01)
    print()

if __name__ == "__main__":
    main()
