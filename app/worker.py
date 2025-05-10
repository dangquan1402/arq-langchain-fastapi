import asyncio
from typing import Dict, List

from arq.connections import RedisSettings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.base import  messages_to_dict, message_to_dict
from langchain_core.messages.utils import messages_from_dict, convert_to_messages
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# Define our worker functions directly at module level for ARQ to find them
async def process_langchain_request(ctx, messages: List[Dict]):
    """
    Process a LangChain request asynchronously
    
    Args:
        ctx: arq context
        messages: List of message dicts with role and content
    
    Returns:
        str: LangChain response
    """
    logger.info(f"Processing LangChain request with {len(messages)} messages")
    try:
        # Initialize LLM (moved from class to function for simplicity)
        llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.0,  # Low temperature for factual responses
            max_tokens=settings.MAX_OUTPUT_TOKENS,
        )
        
        messages = convert_to_messages(messages)
        # Convert messages to the format expected by LangChain
        
        # Process with LLM
        response = await llm.ainvoke(messages)
        
        logger.info("LangChain processing completed")
        return response.content
    except Exception as e:
        logger.error(f"Error in LangChain processing: {str(e)}")
        raise

async def startup(ctx):
    """Run when the worker starts up."""
    logger.info("Worker starting up")

async def shutdown(ctx):
    """Run when the worker shuts down."""
    logger.info("Worker shutting down")

async def health_check():
    """
    Health check for the ARQ worker.
    Returns True if Redis connection is working and the worker is ready.
    """
    try:
        from arq.connections import RedisSettings, create_pool
        redis = await create_pool(RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        ))
        await redis.ping()
        await redis.close()
        return True
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False

# Define WorkerSettings class which ARQ will use directly
class WorkerSettings:
    """
    Worker settings for ARQ.
    This class is used by the ARQ CLI to create and configure the worker.
    """
    functions = [process_langchain_request]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )
    max_jobs = settings.API_CONCURRENCY_LIMIT
    job_timeout = 60  # Timeout for jobs in seconds
    keep_result = 300  # How long to keep job results (seconds)
    max_tries = 3     # Number of retries for failed jobs

# Keep create_worker for backward compatibility
def create_worker():
    """
    Create and configure the ARQ worker (for backward compatibility).
    Returns the worker settings dictionary.
    """
    logger.info("Creating ARQ worker using legacy dictionary approach")
    
    # Convert the class attributes to a dictionary
    return {
        'functions': [process_langchain_request],
        'startup': startup,
        'shutdown': shutdown,
        'redis_settings': RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        ),
        'max_jobs': settings.API_CONCURRENCY_LIMIT,
        'job_timeout': 60,
        'keep_result': 300,
        'max_tries': 3,
        'job_serializer': 'json'  # Changed from 'pickle' to 'json'
    }
