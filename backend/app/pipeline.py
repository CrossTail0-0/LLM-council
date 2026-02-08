import asyncio
import json
import logging
from typing import List, Dict, Any
from app.config import settings
from app.llm_client import llm_client
from app.models import LLMResponse, ReviewResponse, RankingEntry, FinalResponse

logger = logging.getLogger(__name__)


class LLMCouncilPipeline:
    """3-stage pipeline for LLM Council processing"""
    
    def __init__(self):
        self.models = settings.council_models
    
    async def stage_1_initial_responses(self, query: str) -> List[LLMResponse]:
        """
        Stage 1: Get initial responses from all LLMs in parallel
        
        Args:
            query: User's question
            
        Returns:
            List of LLMResponse objects
        """
        logger.info("Stage 1: Getting initial responses from all models")
        
        # Create tasks for parallel execution
        tasks = []
        for idx, model in enumerate(self.models):
            task = llm_client.get_initial_response(model, query)
            tasks.append((model, idx, task))
        
        # Wait for all responses
        responses = []
        for model, idx, task in tasks:
            try:
                response_text = await task
                responses.append(LLMResponse(
                    model_name=model,
                    response=response_text,
                    model_id=chr(65 + idx)  # A, B, C
                ))
            except Exception as e:
                logger.error(f"Error getting response from {model}: {str(e)}")
                # Add error response
                responses.append(LLMResponse(
                    model_name=model,
                    response=f"Error: Failed to get response from this model. {str(e)}",
                    model_id=chr(65 + idx)
                ))
        
        logger.info(f"Stage 1 complete: Received {len(responses)} responses")
        return responses
    
    async def stage_2_cross_review(
        self, 
        query: str, 
        initial_responses: List[LLMResponse]
    ) -> List[ReviewResponse]:
        """
        Stage 2: Each LLM reviews and ranks other LLMs' responses
        
        Args:
            query: Original user query
            initial_responses: List of initial responses from stage 1
            
        Returns:
            List of ReviewResponse objects
        """
        logger.info("Stage 2: Cross-review and ranking")
        
        reviews = []
        
        for reviewer_idx, reviewer_model in enumerate(self.models):
            try:
                # Create anonymized list excluding the reviewer's own response
                anonymized = []
                for resp in initial_responses:
                    # Skip the reviewer's own response
                    if resp.model_name == reviewer_model:
                        continue
                    
                    anonymized.append({
                        "id": resp.model_id,
                        "content": resp.response
                    })
                
                if len(anonymized) < 2:
                    logger.warning(f"Not enough responses for {reviewer_model} to review")
                    continue
                
                # Get review
                review_text = await llm_client.get_review_rankings(
                    reviewer_model, 
                    query, 
                    anonymized
                )
                
                # Parse JSON response
                rankings = self._parse_ranking_response(review_text)
                
                if rankings:
                    reviews.append(ReviewResponse(
                        reviewer_model=reviewer_model,
                        rankings=rankings
                    ))
                else:
                    logger.warning(f"Could not parse rankings from {reviewer_model}")
                
            except Exception as e:
                logger.error(f"Error during review by {reviewer_model}: {str(e)}")
        
        logger.info(f"Stage 2 complete: Received {len(reviews)} reviews")
        return reviews
    
    def _parse_ranking_response(self, response_text: str) -> List[RankingEntry]:
        """
        Parse JSON ranking response from LLM
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            List of RankingEntry objects or empty list if parsing fails
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return []
            
            json_text = response_text[start_idx:end_idx]
            data = json.loads(json_text)
            
            rankings = []
            for ranking_data in data.get('rankings', []):
                rankings.append(RankingEntry(
                    response_id=ranking_data['response_id'],
                    rank=ranking_data['rank'],
                    reasoning=ranking_data['reasoning']
                ))
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error parsing ranking response: {str(e)}")
            return []
    
    async def stage_3_chairman_synthesis(
        self,
        query: str,
        initial_responses: List[LLMResponse],
        reviews: List[ReviewResponse]
    ) -> FinalResponse:
        """
        Stage 3: Chairman synthesizes all responses and reviews
        
        Args:
            query: Original user query
            initial_responses: All initial responses
            reviews: All review rankings
            
        Returns:
            FinalResponse object
        """
        logger.info("Stage 3: Chairman synthesis")
        
        # Prepare data for chairman
        responses_data = [
            {
                "model_id": resp.model_id,
                "model_name": resp.model_name,
                "response": resp.response
            }
            for resp in initial_responses
        ]
        
        reviews_data = [
            {
                "reviewer_model": review.reviewer_model,
                "rankings": [
                    {
                        "response_id": r.response_id,
                        "rank": r.rank,
                        "reasoning": r.reasoning
                    }
                    for r in review.rankings
                ]
            }
            for review in reviews
        ]
        
        # Get chairman's synthesis
        try:
            final_content = await llm_client.get_chairman_synthesis(
                query,
                responses_data,
                reviews_data
            )
            
            return FinalResponse(
                content=final_content,
                chairman_model=settings.chairman_model
            )
            
        except Exception as e:
            logger.error(f"Error during chairman synthesis: {str(e)}")
            # Fallback: return first response
            return FinalResponse(
                content=f"Error during synthesis. Fallback response:\n\n{initial_responses[0].response if initial_responses else 'No responses available.'}",
                chairman_model=settings.chairman_model
            )
    
    async def run_full_pipeline(self, query: str) -> Dict[str, Any]:
        """
        Run the complete 3-stage pipeline
        
        Args:
            query: User's question
            
        Returns:
            Dict containing all stages' results
        """
        import time
        start_time = time.time()
        
        # Stage 1: Initial responses
        stage_1_responses = await self.stage_1_initial_responses(query)
        
        # Stage 2: Cross-review
        stage_2_reviews = await self.stage_2_cross_review(query, stage_1_responses)
        
        # Stage 3: Chairman synthesis
        stage_3_final = await self.stage_3_chairman_synthesis(
            query, 
            stage_1_responses, 
            stage_2_reviews
        )
        
        processing_time = time.time() - start_time
        
        return {
            "query": query,
            "stage_1_responses": [resp.model_dump() for resp in stage_1_responses],
            "stage_2_reviews": [review.model_dump() for review in stage_2_reviews],
            "stage_3_final": stage_3_final.model_dump(),
            "processing_time": round(processing_time, 2)
        }


# Global pipeline instance
pipeline = LLMCouncilPipeline()