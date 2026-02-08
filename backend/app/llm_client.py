import os
from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with HuggingFace Router LLMs"""
    
    def __init__(self):
        """Initialize the OpenAI client with HuggingFace router"""
        self.client = OpenAI(
            base_url=settings.hf_base_url,
            api_key=settings.hf_token or os.environ.get("HF_TOKEN", "")
        )
    
    async def get_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Get completion from a specific model
        
        Args:
            model: Model identifier
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            str: The model's response content
        """
        try:
            logger.info(f"Requesting completion from {model}")
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_content = completion.choices[0].message.content
            logger.info(f"Received response from {model} ({len(response_content)} chars)")
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error getting completion from {model}: {str(e)}")
            raise
    
    async def get_initial_response(self, model: str, query: str) -> str:
        """
        Get initial response to user query
        
        Args:
            model: Model identifier
            query: User's question
            
        Returns:
            str: Model's response
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Provide clear, accurate, and insightful responses to user questions."
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        return await self.get_completion(model, messages)
    
    async def get_review_rankings(
        self, 
        model: str, 
        query: str, 
        anonymized_responses: List[Dict[str, str]]
    ) -> str:
        """
        Get model's ranking of other responses
        
        Args:
            model: Model doing the reviewing
            query: Original user query
            anonymized_responses: List of responses with IDs (anonymized)
            
        Returns:
            str: Model's ranking response
        """
        responses_text = "\n\n".join([
            f"Response {resp['id']}:\n{resp['content']}"
            for resp in anonymized_responses
        ])
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert evaluator of AI responses. You will be given a user query and several anonymized responses from different AI models.

Your task is to rank these responses from best to worst based on:
1. Accuracy and correctness
2. Depth of insight
3. Clarity and organization
4. Completeness

Provide your ranking in the following JSON format:
{
  "rankings": [
    {"response_id": "A", "rank": 1, "reasoning": "why this is ranked first"},
    {"response_id": "B", "rank": 2, "reasoning": "why this is ranked second"},
    {"response_id": "C", "rank": 3, "reasoning": "why this is ranked third"}
  ]
}

Be objective and critical. Provide specific reasoning for each ranking."""
            },
            {
                "role": "user",
                "content": f"Original Query: {query}\n\nResponses to evaluate:\n\n{responses_text}\n\nPlease provide your ranking in JSON format."
            }
        ]
        
        return await self.get_completion(model, messages, temperature=0.3)
    
    async def get_chairman_synthesis(
        self, 
        query: str, 
        responses: List[Dict[str, Any]], 
        reviews: List[Dict[str, Any]]
    ) -> str:
        """
        Get chairman's final synthesized response
        
        Args:
            query: Original user query
            responses: All LLM responses with metadata
            reviews: All review rankings
            
        Returns:
            str: Chairman's synthesized response
        """
        # Format responses
        responses_text = "\n\n".join([
            f"Model {resp['model_id']} ({resp['model_name']}):\n{resp['response']}"
            for resp in responses
        ])
        
        # Format reviews
        reviews_text = "\n\n".join([
            f"Review by {review['reviewer_model']}:\n" + 
            "\n".join([
                f"  - Ranked {r['response_id']} as #{r['rank']}: {r['reasoning']}"
                for r in review['rankings']
            ])
            for review in reviews
        ])
        
        messages = [
            {
                "role": "system",
                "content": """You are the Chairman of the LLM Council. Your role is to synthesize multiple AI responses and their peer reviews into a single, comprehensive, and accurate final answer.

Consider:
1. Points of agreement across responses
2. Unique insights from each model
3. The peer review rankings and reasoning
4. Accuracy and correctness of information

Provide a clear, well-organized final response that represents the best collective wisdom of the council. Do not mention the individual models or the review process - simply provide the best possible answer to the user's question."""
            },
            {
                "role": "user",
                "content": f"""Original Query: {query}

Individual Responses:
{responses_text}

Peer Reviews:
{reviews_text}

Please provide your final synthesized response to the user's query."""
            }
        ]
        
        return await self.get_completion(model=settings.chairman_model, messages=messages, max_tokens=3000)


# Global client instance
llm_client = LLMClient()