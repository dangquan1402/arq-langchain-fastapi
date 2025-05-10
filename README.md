# ARQ-based API with LangChain Integration

This project demonstrates a scalable API using ARQ (Asynchronous Redis Queue) for handling concurrent requests to a LangChain-powered generative AI service.

## Architecture

The project uses a three-tier architecture:
- API service (FastAPI)
- Worker service (ARQ)
- Redis (queue and result storage)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Google API key for Generative AI

### Running the Project

1. Copy `.env.example` to `.env` and add your Google API key:
   ```
   cp .env.example .env
   # Edit .env and add GOOGLE_API_KEY=your-key-here
   ```

2. Start the services with Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the API at http://localhost:8000

## Testing and Monitoring

### Load Testing

You can use the provided test client to send concurrent requests to the API:

```bash
# Run with default settings (100 requests, 10 concurrency)
python tests/test_client.py

# Custom configuration
python tests/test_client.py --concurrency 20 --requests 200 --url http://localhost:8000/langchain/process
```

### Queue Monitoring

Monitor the ARQ queue statistics in real-time:

```bash
# Run with default settings
python tools/monitor_queue.py

# Custom configuration
python tools/monitor_queue.py --interval 0.5 --duration 60
```

### Useful Commands

Check worker logs:
```bash
docker-compose logs -f worker
```

Inspect Redis:
```bash
docker-compose exec redis redis-cli
```

## Project Structure

```
app/
├── core/               # Core functionality
│   └── config.py       # Configuration management
├── main.py             # Application entry point
└── worker.py           # ARQ worker implementation
tests/
└── test_client.py      # Load testing client
tools/
└── monitor_queue.py    # ARQ queue monitoring tool
```

## Troubleshooting

If the worker isn't processing jobs:

1. Check worker logs with `docker-compose logs worker`
2. Verify Redis connection settings in `.env`
3. Ensure Google API key is valid
4. Check if Redis is running with `docker-compose ps redis`

## Development

When developing locally, you can use the mounted volumes to make changes without rebuilding images. The API server uses `--reload` to automatically detect changes.


python tests/test_client.py --concurrency 5 --requests 20 --url http://localhost:8000/chat
