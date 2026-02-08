from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class Stage(str, Enum):
    """Processing stages"""
    INITIAL = "initial"
    REVIEW = "review"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"


@dataclass
class QueryRequest:
    """User query request"""
    query: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(query=data.get("query", ""))
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the request"""
        if not self.query or not self.query.strip():
            return False, "Query cannot be empty"
        return True, None


@dataclass
class LLMResponse:
    """Individual LLM response"""
    model_name: str
    response: str
    model_id: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RankingEntry:
    """Single ranking entry from an LLM"""
    response_id: str
    rank: int
    reasoning: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReviewResponse:
    """LLM's review of other responses"""
    reviewer_model: str
    rankings: List[RankingEntry]
    
    def to_dict(self) -> dict:
        return {
            "reviewer_model": self.reviewer_model,
            "rankings": [r.to_dict() for r in self.rankings]
        }


@dataclass
class FinalResponse:
    """Chairman's final synthesized response"""
    content: str
    chairman_model: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineResponse:
    """Complete pipeline response"""
    query: str
    stage_1_responses: List[LLMResponse]
    stage_2_reviews: List[ReviewResponse]
    stage_3_final: FinalResponse
    processing_time: float
    
    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "stage_1_responses": [r.to_dict() for r in self.stage_1_responses],
            "stage_2_reviews": [r.to_dict() for r in self.stage_2_reviews],
            "stage_3_final": self.stage_3_final.to_dict(),
            "processing_time": self.processing_time
        }


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    models_configured: int
    hf_token_set: bool
    
    def to_dict(self) -> dict:
        return asdict(self)