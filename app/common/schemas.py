from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class BaseConfigSchema(BaseModel):
    """Base configuration schema for all services."""
    concurrency_limit: int = Field(
        default=5,
        description="Maximum number of concurrent operations",
        gt=0, le=20
    )


class BaseRequestSchema(BaseModel):
    """Base request schema with common parameters."""
    pass


class BaseResponseSchema(BaseModel):
    """Base response schema with common response data."""
    processing_time: Optional[float] = Field(
        None,
        description="Time taken to process the request in seconds"
    )


class FileInfoSchema(BaseModel):
    """Common file information schema."""
    filename: str = Field(..., description="Name of the file")
    file_path: Optional[str | Path] = Field(None, description="Path to the file on disk")
