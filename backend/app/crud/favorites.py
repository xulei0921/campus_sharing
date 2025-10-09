from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from .. import models, schemas
from .items import get_item  # 引入物品操作

# 创建收藏（收藏物品）
def create_favorite(db: Session, favorite: schemas.FavoriteCreate, user_id: int):
    """收藏物品"""
    # 检查物品是否存在
    item = get_item(db=db, item_id=favorite.item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查是否已收藏
    existing_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.item_id == favorite.item_id
    ).first()

    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已收藏该物品"
        )

    # 创建收藏对象
    db_favorite = models.Favorite(
        user_id=user_id,
        item_id=favorite.item_id
    )

    # 保存收藏
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)

    return db_favorite

# 获取用户的收藏列表
def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取指定用户的收藏列表"""
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).order_by(models.Favorite.created_at.desc()).offset(skip).limit(limit).all()

# 取消收藏（删除收藏）
def delete_favorite(db: Session, item_id: int, user_id: int):
    """取消收藏物品"""
    # 检查收藏是否存在
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.item_id == item_id
    ).first()

    if not db_favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏该物品"
        )

    db.delete(db_favorite)
    db.commit()

    return {"message": "已取消收藏"}

# 检查物品是否被用户收藏
def is_item_favorited(db: Session, item_id: int, user_id: int):
    """检查物品是否被用户收藏"""
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.item_id == item_id
    ).first()

    return favorite is not None