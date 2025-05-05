"""
FastAPI server for BitNet.cpp application.
Provides API endpoints for model management and local CPU-only inference.
All processing is done locally on the user's machine without requiring any cloud services.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from model_manager import ModelManager
from inference import InferenceEngine

# Create FastAPI app
app = FastAPI(
    title="BitNet.cpp API",
    description="API for BitNet.cpp models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create model manager and inference engine
model_manager = ModelManager()
inference_engine = InferenceEngine(model_manager)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, "server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define API models
class ModelInfo(BaseModel):
    model_id: str
    quant_type: Optional[str] = None

class InferenceRequest(BaseModel):
    model: str
    prompt: str
    n_predict: int = 128
    threads: int = 4
    ctx_size: int = 2048
    temperature: float = 0.8
    conversation: bool = False

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    n_predict: int = 128
    threads: int = 4
    ctx_size: int = 2048
    temperature: float = 0.8
    stream: bool = False

# Define API endpoints
@app.get("/")
async def root():
    """Redirect to static index.html."""
    return {"message": "Welcome to BitNet.cpp API. Visit /docs for API documentation."}

@app.get("/models/available")
async def list_available_models():
    """List all available models from Hugging Face."""
    return model_manager.list_available_models()

@app.get("/models/installed")
async def list_installed_models():
    """List all installed models."""
    return model_manager.list_installed_models()

@app.post("/models/download")
async def download_model(model_info: ModelInfo, background_tasks: BackgroundTasks):
    """Download a model from Hugging Face."""
    # Start download in background
    background_tasks.add_task(
        model_manager.download_model,
        model_info.model_id,
        model_info.quant_type
    )

    return {
        "message": f"Started downloading model {model_info.model_id}. Check /models/installed to see when it's ready."
    }

@app.delete("/models/{model_name}")
async def remove_model(model_name: str):
    """Remove a model."""
    success = model_manager.remove_model(model_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    return {"message": f"Model {model_name} removed successfully"}

@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a model."""
    model_info = model_manager.get_model_info(model_name)
    if model_info is None:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    return model_info

@app.post("/inference")
async def run_inference(request: InferenceRequest):
    """Run inference on a model."""
    try:
        response = inference_engine.run_inference(
            model_name=request.model,
            prompt=request.prompt,
            n_predict=request.n_predict,
            threads=request.threads,
            ctx_size=request.ctx_size,
            temperature=request.temperature,
            conversation=request.conversation
        )

        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inference/stream")
async def stream_inference(request: InferenceRequest):
    """Stream inference results from a model."""
    try:
        async def generate():
            # Create generator for streaming response
            queue = []

            def callback(chunk: str):
                queue.append(chunk)

            # Start inference in background
            inference_engine.stream_inference(
                model_name=request.model,
                prompt=request.prompt,
                callback=callback,
                n_predict=request.n_predict,
                threads=request.threads,
                ctx_size=request.ctx_size,
                temperature=request.temperature,
                conversation=request.conversation
            )

            # Stream results
            while True:
                if queue:
                    chunk = queue.pop(0)
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
                else:
                    break

            # End stream
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Generate a chat completion."""
    try:
        if request.stream:
            async def generate():
                # Create generator for streaming response
                def callback(response: Dict[str, Any]):
                    yield f"data: {json.dumps(response)}\n\n"

                # Start inference in background
                inference_engine.stream_chat_completion(
                    model_name=request.model,
                    messages=[msg.dict() for msg in request.messages],
                    callback=callback,
                    n_predict=request.n_predict,
                    threads=request.threads,
                    ctx_size=request.ctx_size,
                    temperature=request.temperature
                )

                # End stream
                yield "data: [DONE]\n\n"

            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            response = inference_engine.chat_completion(
                model_name=request.model,
                messages=[msg.dict() for msg in request.messages],
                n_predict=request.n_predict,
                threads=request.threads,
                ctx_size=request.ctx_size,
                temperature=request.temperature
            )

            return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
