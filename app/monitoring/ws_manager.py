import asyncio
from typing import Dict, Set
from fastapi import WebSocket
import json


class WebSocketManager:
    """WebSocket连接管理器 - 单例模式"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.active_connections: Dict[str, Set[WebSocket]] = {}
        return cls._instance

    async def connect(self, user_id: str, websocket: WebSocket):
        """建立WebSocket连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: dict):
        """发送个人消息"""
        if user_id in self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False, default=str)
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message_str)
                except Exception:
                    disconnected.append(websocket)
            # 清理断开的连接
            for ws in disconnected:
                self.disconnect(user_id, ws)

    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        message_str = json.dumps(message, ensure_ascii=False, default=str)
        for user_id, connections in list(self.active_connections.items()):
            for websocket in connections:
                try:
                    await websocket.send_text(message_str)
                except Exception:
                    self.disconnect(user_id, websocket)

    def get_online_count(self) -> int:
        """获取在线用户数"""
        return len(self.active_connections)


# 全局单例
ws_manager = WebSocketManager()
