"""
FastAPI application main entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api import auth
from app.models.registry import ModelRegistry
from app.models.translator import TranslationService
from app.models.generator import GenerationService
from app.models.asr import WhisperASRService
from app.config import MODEL_CONFIGS
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Transformer Model API",
    description="API for Shona-English translation, Shona text generation, and ASR",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model registry and services
registry = ModelRegistry(device='auto')
translation_service = TranslationService(registry)
generation_service = GenerationService(registry)

# Initialize ASR service (optional - only if model exists)
asr_service = None
try:
    asr_service = WhisperASRService(device='cpu')  # Use CPU for Mac
    logger.info(f"ASR service initialized with model: {asr_service.base_model_name}")
except Exception as e:
    logger.warning(f"ASR service not available: {e}")

# Register all models and inject services
for config in MODEL_CONFIGS:
    registry.register_model(config)

routes.set_services(registry, translation_service, generation_service, asr_service)

# Include routers
app.include_router(routes.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Transformer Model API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "models": "/api/models",
            "translate": "/api/translate",
            "generate": "/api/generate",
            "transcribe": "/api/transcribe" if asr_service else None
        }
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
