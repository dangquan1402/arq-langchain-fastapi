import os
from typing import Dict, List
from contextlib import asynccontextmanager

from arq.connections import RedisSettings, create_pool
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel
from langchain_core.messages.base import BaseMessage, messages_to_dict
from langchain_core.messages.utils import convert_to_messages
from app.core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Redis
    app.state.redis = await create_pool(RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    ))
    logger.info("Connected to Redis")
    
    yield
    
    # Shutdown: Close Redis connection
    await app.state.redis.close()
    logger.info("Disconnected from Redis")

app = FastAPI(title="LangChain API with arq", lifespan=lifespan)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat", response_model=Dict)
async def chat(request: ChatRequest):
    try:
        # Enqueue the task to arq worker
        job = await app.state.redis.enqueue_job(
            'process_langchain_request', 
            messages=request.model_dump().get('messages')
        )
        
        # Wait for the result with a timeout
        result = await job.result(timeout=30)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Processing timed out")
            
        return {"result": result}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
