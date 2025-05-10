import asyncio
import argparse
import time
from typing import List, Dict
import aiohttp
import json
from loguru import logger

async def send_request(session, url: str, messages: List[Dict], request_id: int):
    """Send a single request to the API and log the response time."""
    start_time = time.time()
    try:
        async with session.post(
            url, 
            json={"messages": messages},
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            elapsed = time.time() - start_time
            logger.info(f"Request {request_id} completed in {elapsed:.2f}s - Status: {response.status}")
            logger.info(f"Response {request_id}: {json.dumps(result, indent=2)}")
            return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Request {request_id} failed after {elapsed:.2f}s: {str(e)}")
        return {"error": str(e)}

async def run_load_test(concurrency: int, total_requests: int, url: str):
    """Run a load test with the specified concurrency level and request count."""
    logger.info(f"Starting load test: {total_requests} total requests with concurrency {concurrency}")
    
    # Sample messages for the LLM
    messages = [
        {"role": "user", "content": "What are the benefits of using FastAPI for backend development?"}
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(total_requests):
            tasks.append(send_request(session, url, messages, i+1))
            # If we've created enough tasks to match our concurrency limit,
            # or if this is the last batch, execute them
            if len(tasks) >= concurrency or i == total_requests - 1:
                await asyncio.gather(*tasks)
                tasks = []  # Reset tasks for the next batch
                
    logger.info(f"Load test completed: {total_requests} requests sent")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load testing tool for ARQ-based API")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests to send")
    parser.add_argument("--url", type=str, default="http://localhost:8000/langchain/process", 
                        help="API endpoint URL")
    
    args = parser.parse_args()
    
    logger.info(f"Load test configuration: {args.requests} requests, {args.concurrency} concurrency")
    asyncio.run(run_load_test(args.concurrency, args.requests, args.url))
