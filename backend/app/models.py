from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class Stage(str, Enum):
    """Processing stages"""
    INITIAL = "initial"
    REVIEW = "review"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"


class QueryRequest(BaseModel):
    """User query request"""
    query: str = Field(..., min_length=1, description="User's question or prompt")


class LLMResponse(BaseModel):
    """Individual LLM response"""
    model_name: str = Field(..., description="Name of the LLM model")
    response: str = Field(..., description="The LLM's response text")
    model_id: str = Field(..., description="Unique identifier for this model")


class RankingEntry(BaseModel):
    """Single ranking entry from an LLM"""
    response_id: str = Field(..., description="ID of the response being ranked")
    rank: int = Field(..., ge=1, description="Rank position (1 is best)")
    reasoning: str = Field(..., description="Why this rank was assigned")


class ReviewResponse(BaseModel):
    """LLM's review of other responses"""
    reviewer_model: str = Field(..., description="Model doing the reviewing")
    rankings: List[RankingEntry] = Field(..., description="Ranked list of responses")


class FinalResponse(BaseModel):
    """Chairman's final synthesized response"""
    content: str = Field(..., description="The final synthesized answer")
    chairman_model: str = Field(..., description="Model that acted as chairman")


class PipelineResponse(BaseModel):
    """Complete pipeline response"""
    query: str = Field(..., description="Original user query")
    stage_1_responses: List[LLMResponse] = Field(..., description="Individual LLM responses")
    stage_2_reviews: List[ReviewResponse] = Field(..., description="Cross-review rankings")
    stage_3_final: FinalResponse = Field(..., description="Final synthesized response")
    processing_time: float = Field(..., description="Total processing time in seconds")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    models_configured: int
    hf_token_set: bool