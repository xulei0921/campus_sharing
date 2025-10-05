from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Annotated
import json
from datetime import datetime

from .. import schemas, dependencies
from ..database import get_db
from ..crud import chats as chats_crud

# 创建路由实例
router = APIRouter()

# 用于管理WebSocket连接
class ConnectionManager:
    def __init__(self):
        # 存储活动连接: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """向指定用户发送消息"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """向所有连接的用户广播消息"""
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))

# 创建连接管理器实例
manager = ConnectionManager()

# 发送聊天消息
@router.post("/", response_model=schemas.ChatResponse)
async def create_chat(
    chat: schemas.ChatCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        发送聊天消息（需要登录）

        参数：
        - chat: 聊天消息内容

        返回：
        - 发送的消息详情
    """
    # 创建消息
    db_chat = chats_crud.create_chat(db=db, chat=chat, sender_id=current_user.id)

    # 准备要发送的消息数据
    message_data = {
        "id": db_chat.id,
        "item_id": db_chat.item_id,
        "sender_id": db_chat.sender_id,
        "receiver_id": db_chat.receiver_id,
        "message": db_chat.message,
        "created_at": db_chat.created_at.isoformat(),
        "sender": {
            "id": current_user.id,
            "username": current_user.username,
            "avatar": current_user.avatar
        }
    }

    # 通过WebSocket实时发送给接收者
    await manager.send_personal_message(message_data, db_chat.receiver_id)

    return db_chat


# 获取物品的聊天记录
@router.get("/item/{item_id}", response_model=List[schemas.ChatResponse])
def read_item_chats(
        item_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
    获取指定物品的聊天记录（需要登录）

    参数：
    - item_id: 物品ID
    - skip: 跳过前n条记录（分页）
    - limit: 最多返回n条记录

    返回：
    - 聊天记录列表
    """
    return chats_crud.get_item_chats(
        db,
        item_id=item_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# 获取用户的所有聊天会话
@router.get("/conversations")
def read_user_conversations(
        db: Session = Depends(get_db),
        current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
    获取用户参与的所有聊天会话（需要登录）

    返回：
    - 聊天会话列表，每个会话包含物品信息、最后一条消息和对方用户信息
    """
    return chats_crud.get_user_chats(db, user_id=current_user.id)


# WebSocket连接端点
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: int,
        token: str = Depends(dependencies.oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    WebSocket连接端点，用于实时接收消息

    参数：
    - user_id: 用户ID
    - token: 认证令牌
    """
    # 验证用户身份
    try:
        # 使用已有的依赖项验证用户
        current_user = dependencies.get_current_user(token=token, db=db)

        # 确保用户ID与令牌中的一致
        if current_user.id != user_id:
            await websocket.close(code=1008)  # 政策原因关闭
            return

    except HTTPException:
        await websocket.close(code=1008)  # 认证失败关闭
        return

    # 建立连接
    await manager.connect(user_id, websocket)

    try:
        while True:
            # 保持连接，等待可能的消息（我们这里只接收，不处理）
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        # 断开连接时清理
        manager.disconnect(user_id)