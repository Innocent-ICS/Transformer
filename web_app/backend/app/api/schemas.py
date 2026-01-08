"""
Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


# Translation schemas
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    model_id: str = Field(default="translation-final", description="Model ID to use")
    max_length: int = Field(default=100, description="Maximum translation length")


class TranslationResponse(BaseModel):
    translation: str
    model_used: str
    inference_time_ms: int
    source_text: str


# Generation schemas
class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="Prompt for text generation")
    model_id: str = Field(default="shona-100K-final", description="Model ID to use")
    max_length: int = Field(default=100, description="Maximum length to generate")
    temperature: float = Field(default=0.8, ge=0.1, le=2.0, description="Sampling temperature")


class GenerationResponse(BaseModel):
    generated_text: str
    model_used: str
    prompt: str
    temperature: float
    max_length: int
    inference_time_ms: int


# Model schemas
class ModelInfo(BaseModel):
    model_id: str
    type: str
    metadata: Dict[str, Any]
    loaded: bool


class ModelListResponse(BaseModel):
    models: List[ModelInfo]


class ModelDetailResponse(BaseModel):
    model_id: str
    type: str
    metadata: Dict[str, Any]
    config: Dict[str, Any]
    loaded: bool


# Health check
class HealthResponse(BaseModel):
    status: str
    device: str
    loaded_models: int


# Error response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
