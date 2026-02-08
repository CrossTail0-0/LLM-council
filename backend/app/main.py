from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.models import QueryRequest, HealthResponse
from app.pipeline import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    logger.info("Starting LLM Council API...")
    logger.info(f"Configured models: {settings.council_models}")
    logger.info(f"Chairman model: {settings.chairman_model}")
    yield
    logger.info("Shutting down LLM Council API...")


# Create FastAPI app
app = FastAPI(
    title="LLM Council API",
    description="Multi-LLM consensus system with cross-review and synthesis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "LLM Council API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    health = HealthResponse(
        status="healthy",
        models_configured=len(settings.council_models),
        hf_token_set=bool(settings.hf_token)
    )
    return health.to_dict()


@app.post("/query", tags=["Query"])
async def process_query(request: Request):
    """
    Process a user query through the 3-stage LLM Council pipeline
    
    Stages:
    1. Initial responses from all LLMs
    2. Cross-review and ranking
    3. Chairman synthesis
    
    Args:
        request: HTTP request containing JSON with 'query' field
        
    Returns:
        Dict with all stages' results
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Create and validate QueryRequest
        query_req = QueryRequest.from_dict(body)
        is_valid, error_msg = query_req.validate()
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Received query: {query_req.query[:100]}...")
        
        if not settings.hf_token:
            raise HTTPException(
                status_code=500,
                detail="HuggingFace token not configured. Please set HF_TOKEN environment variable."
            )
        
        # Run the pipeline
        result = await pipeline.run_full_pipeline(query_req.query)
        
        logger.info(f"Pipeline complete in {result['processing_time']}s")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )