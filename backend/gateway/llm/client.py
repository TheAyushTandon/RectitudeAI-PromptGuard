import httpx
import asyncio
import uuid
from datetime import datetime
from abc import ABC, abstractmethod
from fastapi import HTTPException
from backend.gateway.config import settings
from backend.models.responses import InferenceResponse
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> InferenceResponse:
        pass

class OllamaClient(BaseLLMClient):
    def __init__(self):
        self.base_url = settings.ollama_base_url or "http://localhost:11434"
        self.model = "mistral:instruct"
        self.max_retries = 3

    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> InferenceResponse:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    return InferenceResponse(
                        response=result["response"],
                        tool_calls=[],
                        metadata={"model": self.model, "attempts": attempt + 1},
                        request_id=str(uuid.uuid4()),
                        timestamp=datetime.utcnow()
                    )
                else:
                    logger.error(f"Ollama returned error {response.status_code}: {response.text}")
                    raise HTTPException(status_code=503, detail="Ollama service returned an error")

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning(f"Ollama connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
                else:
                    logger.error("All Ollama connection retries failed.")
                    raise HTTPException(
                        status_code=503, 
                        detail="LLM Service (Ollama) is currently unavailable. Please ensure it is running."
                    )
            except Exception as e:
                logger.error(f"Unexpected error in OllamaClient: {str(e)}")
                raise HTTPException(status_code=500, detail="An unexpected error occurred during LLM generation")

def get_llm_client() -> BaseLLMClient:
    if settings.llm_provider == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")