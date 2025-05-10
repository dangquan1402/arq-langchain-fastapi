FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port for FastAPI
EXPOSE 8000

# The CMD will be overridden by docker-compose for each service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
