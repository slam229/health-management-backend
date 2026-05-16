"""Stable Diffusion API客户端"""
import httpx
from typing import Optional
from config import settings


class SDClient:
    """SD WebUI API封装"""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or settings.SD_API_URL
    
    async def txt2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        **kwargs
    ) -> dict:
        """
        发送文生图请求
        
        Returns:
            {"images": [...], "parameters": {...}, "info": {...}}
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/sdapi/v1/txt2img",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return {"images": [], "error": "SD API unavailable"}


# 全局单例
sd_client = SDClient()
