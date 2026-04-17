import httpx
import asyncio
import uuid
from typing import Optional, List
from datetime import datetime
from abc import ABC, abstractmethod
from fastapi import HTTPException
from backend.gateway.config import settings
from backend.models.responses import InferenceResponse
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> InferenceResponse:
        pass

class MockLLMClient(BaseLLMClient):
    """
    A lightweight mock client for demonstration and testing.
    Allows testing the security pipeline without a live LLM connection.
    """
    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> InferenceResponse:
        # If messages provided, use the last user message as prompt
        if messages and not prompt:
            prompt = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        
        prompt = prompt or ""
        await asyncio.sleep(0.5)  # Simulate network latency
        
        # Simple rule-based mock responses for demo
        p_lower = prompt.lower()
        if "prime numbers" in p_lower:
            response = "The first 5 prime numbers are 2, 3, 5, 7, and 11. Their sum is 28."
        elif "engineering" in p_lower:
            response = "The Engineering department currently has 5 members: Alice, Bob, Charlie, David, and Eve."
        elif "email" in p_lower:
            response = "I have drafted the email as requested. Should I send it to HR@acmecorp.com now?"
        elif system_prompt and "audit" in system_prompt.lower():
            response = "As an Audit Agent, I have reviewed the data and found no security anomalies."
        else:
            response =f"This is a SECURE response from the Rectitude.AI Mock LLM Client. I received your prompt: '{prompt[:30]}...'"
            
        return InferenceResponse(
            response=response,
            tool_calls=[],
            metadata={"model": "mock-security-logic", "simulated": True},
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )

class OllamaClient(BaseLLMClient):
    def __init__(self, model: Optional[str] = None):
        self.base_url = settings.ollama_base_url or "http://localhost:11434"
        self.model = model or settings.ollama_model or settings.default_model or "llama3:8b"
        self.max_retries = 3

    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> InferenceResponse:
        url = f"{self.base_url}/api/generate"
        
        # Format messages or prompt
        final_prompt = ""
        if messages:
            for msg in messages:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                final_prompt += f"### {role} ###\n{content}\n"
            if system_prompt:
                final_prompt = f"### SYSTEM ###\n{system_prompt}\n" + final_prompt
            final_prompt += "Assistant:"
        else:
            final_prompt = prompt or ""
            if system_prompt:
                final_prompt = (
                    f"### SYSTEM INSTRUCTIONS ###\n{system_prompt}\n"
                    f"### END SYSTEM INSTRUCTIONS ###\n\n"
                    f"### USER INPUT ###\n{prompt}\n"
                    f"### END USER INPUT ###\n\n"
                    f"Assistant:"
                )

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            },
            "stream": False
        }

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    return InferenceResponse(
                        response=result["response"],
                        tool_calls=[],
                        metadata={"model": self.model, "attempts": attempt + 1, "optimized": True},
                        request_id=str(uuid.uuid4()),
                        timestamp=datetime.utcnow()
                    )
                else:
                    logger.error(f"Ollama returned error {response.status_code}: {response.text}")
                    raise HTTPException(status_code=503, detail=f"Ollama service returned error {response.status_code}")

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning(f"Ollama connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise HTTPException(
                        status_code=503, 
                        detail="LLM Service (Ollama) is unavailable after retries."
                    )
            except Exception as e:
                logger.error(f"Unexpected error in OllamaClient: {str(e)}")
                raise HTTPException(status_code=500, detail="An unexpected error occurred during LLM generation")

    async def list_models(self) -> List[str]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

class GroqClient(BaseLLMClient):
    """
    High-speed inference via Groq (OpenAI-compatible API).
    """
    def __init__(self, model: Optional[str] = None):
        self.api_key = settings.groq_api_key
        # Protect against Ollama-style models (containing ':') being sent from frontend cache
        if model and ":" in model:
            logger.warning(f"Invalid model '{model}' for Groq provider. Falling back to {settings.groq_model}")
            self.model = settings.groq_model
        else:
            self.model = model or settings.groq_model or "llama-3.3-70b-versatile"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> InferenceResponse:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        final_messages = []
        if messages:
            if system_prompt and not any(m.get("role") == "system" for m in messages):
                final_messages.append({"role": "system", "content": system_prompt})
            final_messages.extend(messages)
        else:
            if system_prompt:
                final_messages.append({"role": "system", "content": system_prompt})
            if prompt:
                final_messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": final_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return InferenceResponse(
                    response=result["choices"][0]["message"]["content"],
                    tool_calls=[],
                    metadata={"model": self.model, "provider": "groq", "speed": "high"},
                    request_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow()
                )
            else:
                logger.error(f"Groq API error {response.status_code}: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Groq Service error: {response.text}")

        except Exception as e:
            logger.error(f"Unexpected error in GroqClient: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate response from Groq")

    async def list_models(self) -> List[str]:
        """Returns a list of supported Groq models for selection."""
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "gemma2-9b-it"
        ]

class GeminiClient(BaseLLMClient):
    """
    Direct integration with Google Gemini API via REST.
    """
    def __init__(self, model: Optional[str] = None):
        self.api_key = settings.gemini_api_key
        self.model = model or settings.gemini_model or "gemini-2.0-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1500, 
        temperature: float = 0.7
    ) -> InferenceResponse:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        # Build contents
        contents = []
        if messages:
            for msg in messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        else:
            if prompt:
                contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return InferenceResponse(
                    response=text,
                    tool_calls=[],
                    metadata={"model": self.model, "provider": "gemini"},
                    request_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow()
                )
            else:
                logger.error(f"Gemini API error {response.status_code}: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Gemini Service error: {response.text}")

        except Exception as e:
            logger.error(f"Unexpected error in GeminiClient: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate response from Gemini")

    async def list_models(self) -> List[str]:
        return ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

class TextualLLMClient(OllamaClient):
    """
    Specialized for high-accuracy textual tasks: writing, editing, and analysis.
    Uses centralized system prompt management.
    """
    def __init__(self, model: Optional[str] = None):
        super().__init__(model=model or settings.ollama_model)

    async def generate(
        self, 
        prompt: Optional[str] = None, 
        system_prompt: Optional[str] = None, 
        messages: Optional[List[dict]] = None,
        max_tokens: int = 1500, 
        temperature: float = 0.3
    ) -> InferenceResponse:
        # Fallback to default textual persona if none provided by the agent
        effective_system = system_prompt or "You are a professional text editor and analyzer. Accuracy and clarity are paramount."
        return await super().generate(prompt=prompt, system_prompt=effective_system, messages=messages, max_tokens=max_tokens, temperature=temperature)


def get_llm_client(client_type: str = "default", model_name: Optional[str] = None) -> BaseLLMClient:
    provider = settings.llm_provider.lower()
    
    if provider == "ollama":
        if client_type == "textual":
            return TextualLLMClient(model=model_name)
        return OllamaClient(model=model_name)
    elif provider == "groq":
        # Groq handles textual tasks well enough with the versatile model
        return GroqClient(model=model_name)
    elif provider == "gemini":
        return GeminiClient(model=model_name)
    elif settings.llm_provider == "mock":
        return MockLLMClient()
    else:
        # Fallback to MockLLM if requested provider is unavailable or missing keys
        provider = settings.llm_provider
        if provider == "openai" and not settings.openai_api_key:
            logger.warning("OpenAI Key missing, falling back to MockLLM")
        return MockLLMClient()