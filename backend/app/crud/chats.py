from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from .. import models, schemas

# 创建聊天消息
def create_chat(db: Session, chat: schemas.ChatCreate, sender_id: int):
    # 检查物品是否存在
    item = db.query(models.Item).filter(models.Item.id == chat.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查接收者是否存在
    receiver = db.query(models.User).filter(models.User.id == chat.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="接收用户不存在"
        )

    # 检查不能给自己发消息
    if sender_id == chat.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能给自己发送消息"
        )

    # 检查是否有权限（只能给物品的所有者发消息，或物品所有者可以回复）
    if not (item.user_id == chat.receiver_id or item.user_id == sender_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限发送此消息"
        )

    # 创建消息对象
    db_chat = models.Chat(
        item_id=chat.item_id,
        sender_id=sender_id,
        receiver_id=chat.receiver_id,
        message=chat.message
    )

    # 保存消息
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return db_chat

# 获取物品的聊天记录
def get_item_chats(db: Session, item_id: int, user_id: int, skip: int = 0, limit: int = 100):
    # 获取指定物品的聊天记录（只能查看自己参与的）
    # 检查物品是否存在
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查是否有权限（必须是物品所有者或消息参与者）
    if item.user_id != user_id:
        # 检查是否是消息的发送者或接收者
        has_access = db.query(models.Chat).filter(
            models.Chat.item_id == item_id,
            (models.Chat.sender_id == user_id) | (models.Chat.receiver_id == user_id)
        ).first()

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此聊天记录"
            )

    # 查询聊天记录（按时间升序，oldest first)
    return db.query(models.Chat).filter(
        models.Chat.item_id == item_id
    ).order_by(models.Chat.created_at).offset(skip).limit(limit).all()

# 获取所有用户的聊天会话
def get_user_chats(db: Session, user_id: int):
    # 获取用户参与的所有聊天会话（按物品分组）
    # 查询用户参与的所有物品ID
    subquery = db.query(
        models.Chat.item_id
    ).filter(
        (models.Chat.sender_id == user_id) | (models.Chat.receiver_id == user_id)
    ).distinct()

    # 获取这些物品的信息以及最后一条消息
    conversations = []
    for item_id in subquery:
        item_id = item_id[0]
        item = db.query(models.Item).filter(models.Item.id == item_id).first()

        # 获取最后一条消息
        last_message = db.query(models.Chat).filter(
            models.Chat.item_id == item_id,
            (models.Chat.sender_id == user_id) | (models.Chat.receiver_id == user_id)
        ).order_by(models.Chat.created_at.desc()).first()

        # 获取对方用户信息
        other_user_id = item.user_id if item.user_id != user_id else (
            last_message.sender_id if last_message.sender_id != user_id else last_message.receiver_id
        )
        other_user = db.query(models.User).filter(models.User.id == other_user_id).first()

        conversations.append({
            "item": item,
            "last_message": last_message,
            "other_user": other_user
        })

    # 按最后一条消息时间倒序排序
    return sorted(conversations, key=lambda x:x["last_message"].created_at, reverse=True)
