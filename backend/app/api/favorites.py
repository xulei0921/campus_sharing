from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, dependencies
from ..database import get_db
from ..crud import favorites as favorites_crud

# 创建路由实例
router = APIRouter()

# 收藏物品
@router.post("/", response_model=schemas.FavoriteResponse, status_code=status.HTTP_201_CREATED)
def create_favorite(
    favorite: schemas.FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        收藏物品（需要登录）

        参数：
        - favorite: 收藏信息（物品ID）

        返回：
        - 新创建的收藏详情
    """
    return favorites_crud.create_favorite(
        db=db,
        favorite=favorite,
        user_id=current_user.id
    )

# 获取用户的收藏列表
@router.get("/", response_model=List[schemas.FavoriteResponse])
def read_user_favorites(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取当前用户的收藏列表（需要登录）

        参数：
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录

        返回：
        - 收藏列表
    """
    return favorites_crud.get_user_favorites(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

# 取消收藏
@router.delete("/item/{item_id}")
def delete_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        取消收藏物品（需要登录）

        参数：
        - item_id: 物品ID

        返回：
        - 取消收藏的提示信息
    """
    return favorites_crud.delete_favorite(
        db=db,
        item_id=item_id,
        user_id=current_user.id
    )

# 检查物品是否被收藏
@router.get("/item/{item_id}/check")
def check_item_favorited(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        检查物品是否被当前用户收藏（需要登录）

        参数：
        - item_id: 物品ID

        返回：
        - 是否收藏的布尔值
    """
    is_favorited = favorites_crud.is_item_favorited(
        db=db,
        item_id=item_id,
        user_id=current_user.id
    )

    return {"is_favorited": is_favorited}