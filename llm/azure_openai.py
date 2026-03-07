import httpx
import json
from typing import AsyncIterator, Optional, Any
from .base import LLMProvider
from .response import ChatResponse, StreamChunk


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI 适配器"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-02-15-preview",
        timeout: int = 120
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.endpoint,
                timeout=self.timeout,
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        return self._client
    
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        include_reasoning: bool = True,
        **kwargs
    ) -> ChatResponse:
        client = await self._get_client()
        
        url = f"/openai/deployments/{self.deployment_name}/chat/completions"
        params = {"api-version": self.api_version}
        
        payload = {"messages": messages}
        if tools:
            payload["tools"] = tools
        
        response = await client.post(url, params=params, json=payload)
        response.raise_for_status()
        raw_response = response.json()
        
        choice = raw_response.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        content = message.get("content", "")
        reasoning = None
        tool_calls = message.get("tool_calls")
        
        if include_reasoning:
            reasoning = message.get("reasoning_content") or message.get("reasoning")
        
        return ChatResponse(
            content=content,
            reasoning=reasoning,
            tool_calls=tool_calls,
            raw_response=raw_response
        )
    
    async def stream_chat(
        self,
        messages: list[dict],
        include_reasoning: bool = True,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        client = await self._get_client()
        
        url = f"/openai/deployments/{self.deployment_name}/chat/completions"
        params = {"api-version": self.api_version}
        
        payload = {
            "messages": messages,
            "stream": True
        }
        
        async with client.stream("POST", url, params=params, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        yield StreamChunk(is_finished=True)
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        
                        content = delta.get("content", "")
                        reasoning = ""
                        
                        if include_reasoning:
                            reasoning = delta.get("reasoning_content", "") or delta.get("reasoning", "")
                        
                        yield StreamChunk(
                            content=content,
                            reasoning=reasoning,
                            is_finished=False
                        )
                    except json.JSONDecodeError:
                        continue
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
