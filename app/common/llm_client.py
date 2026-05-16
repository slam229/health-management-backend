"""统一L LM客户端 - DeepSeek API封装"""
import httpx
from typing import Optional, Dict, Any
from config import settings


class LLMClient:
    """DeepSeek API统一调用封装"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.api_url = api_url or settings.DEEPSEEK_API_URL
        self.model = "deepseek-chat"
    
    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送对话请求
        
        Args:
            messages: [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            {"content": "...", "usage": {...}, "model": "..."}
        """
        if not self.api_key:
            # Mock模式
            return self._mock_response(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "model": self.model
                }
        except httpx.HTTPError as e:
            # 降级处理
            return self._mock_response(messages)
    
    def _mock_response(self, messages: list) -> Dict[str, Any]:
        """Mock响应 - API未配置时使用"""
        return {
            "content": '{"risk_level": "medium", "risk_score": 0.55, "summary": "当前健康状况处于中等风险水平，建议加强日常监测。"}',
            "usage": {"total_tokens": 500},
            "model": "mock"
        }


# 全局单例
llm_client = LLMClient()
