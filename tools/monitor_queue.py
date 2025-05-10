import asyncio
import argparse
import time
from datetime import datetime
from arq.connections import RedisSettings, create_pool
from redis.asyncio import Redis
import os
import sys

# Add the project root to the path to import settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import get_settings

settings = get_settings()

class ArqMonitor:
    def __init__(self, queue_name="arq:queue", redis_settings=None):
        """Initialize the ARQ monitor with Redis connection settings."""
        self.queue_name = queue_name
        self.redis_settings = redis_settings or RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await create_pool(self.redis_settings)
        
    async def get_queue_stats(self):
        """Get current queue statistics."""
        if not self.redis:
            await self.connect()
            
        # Get queue length
        queue_length = await self.redis.llen(self.queue_name)
        
        # Get processing jobs
        processing_key = f"{self.queue_name}:processing"
        processing_jobs = await self.redis.hlen(processing_key)
        
        # Get completed job count
        result_key_pattern = f"{self.queue_name}:result:*"
        complete_keys = await self.redis.keys(result_key_pattern)
        complete_jobs = len(complete_keys)
        
        # Get failed jobs if any
        failed_key = f"{self.queue_name}:failed"
        failed_jobs = await self.redis.zcard(failed_key)
        
        return {
            "enqueued": queue_length,
            "processing": processing_jobs,
            "completed": complete_jobs,
            "failed": failed_jobs,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
    async def print_stats(self, interval=1, duration=None):
        """Print queue statistics at regular intervals."""
        start_time = time.time()
        iteration = 0
        
        try:
            print(f"{'Time':^10} | {'Enqueued':^10} | {'Processing':^10} | {'Completed':^10} | {'Failed':^10}")
            print("-" * 60)
            
            while True:
                if duration and time.time() - start_time > duration:
                    break
                    
                stats = await self.get_queue_stats()
                print(f"{stats['timestamp']:^10} | {stats['enqueued']:^10} | {stats['processing']:^10} | "
                      f"{stats['completed']:^10} | {stats['failed']:^10}")
                
                iteration += 1
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        finally:
            if self.redis:
                await self.redis.close()

async def main(args):
    """Main function to run the monitor."""
    monitor = ArqMonitor(
        queue_name=args.queue_name,
        redis_settings=RedisSettings(
            host=args.redis_host,
            port=args.redis_port
        )
    )
    
    await monitor.print_stats(interval=args.interval, duration=args.duration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor ARQ queue statistics")
    parser.add_argument("--queue-name", default="arq:queue", help="ARQ queue name")
    parser.add_argument("--redis-host", default=settings.REDIS_HOST, help="Redis host")
    parser.add_argument("--redis-port", type=int, default=settings.REDIS_PORT, help="Redis port")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval in seconds")
    parser.add_argument("--duration", type=int, default=None, 
                        help="Duration to monitor in seconds (default: run until interrupted)")
    
    args = parser.parse_args()
    asyncio.run(main(args))
