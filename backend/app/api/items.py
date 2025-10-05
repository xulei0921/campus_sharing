from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import  schemas, dependencies
from ..database import get_db
from ..crud import items as items_crud

# 创建路由实例
router = APIRouter()

# 创建物品
@router.post("/", response_model=schemas.ItemDetailResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        发布新物品（需要登录）

        参数：
        - item: 物品信息（标题、描述、价格等）

        返回：
        - 新创建的物品详情
    """
    # 发布新物品（需要登录）
    return items_crud.create_item(db=db, item=item, user_id=current_user.id)

# 获取物品列表（支持筛选）
@router.get("/", response_model=List[schemas.ItemBriefResponse])
def read_items(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[schemas.ItemStatus] = None,
    db: Session = Depends(get_db)
):
    """
        获取物品列表（无需登录）

        参数：
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录
        - category_id: 按分类筛选
        - search: 按关键词搜索
        - min_price: 最低价格
        - max_price: 最高价格
        - status: 物品状态

        返回：
        - 物品列表
    """
    # 获取物品列表（无需登录）
    items = items_crud.get_items(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        status=status
    )
    return items

# 获取用户发布的物品
@router.get("/my-items", response_model=List[schemas.ItemBriefResponse])
def read_my_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取当前用户发布的物品（需要登录）

        参数：
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录

        返回：
        - 当前用户发布的物品列表
    """
    # 获取当前用户发布的物品（需要登录）
    items = items_crud.get_user_items(db=db, skip=skip, limit=limit, user_id=current_user.id)
    return items

# 获取物品详情
@router.get("/{item_id}", response_model=schemas.ItemDetailResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
        根据ID获取物品详情（无需登录）

        参数：
        - item_id: 物品ID

        返回：
        - 物品详细信息
    """
    # 根据ID获取物品详情（无需登录）
    db_item = items_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="物品不存在")

    return db_item

# 更新物品
@router.put("/{item_id}", response_model=schemas.ItemDetailResponse)
def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        更新物品信息（需要登录，只能更新自己的物品）

        参数：
        - item_id: 物品ID
        - item: 要更新的物品信息

        返回：
        - 更新后的物品信息
    """
    # 更新物品信息（需要登录，只能更新自己的物品）
    return items_crud.update_item(
        item_id=item_id,
        db=db,
        user_id=current_user.id,
        item_update=item
    )

# 删除物品
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        删除物品（需要登录，只能删除自己的物品）

        参数：
        - item_id: 物品ID

        返回：
        - 成功删除的提示信息
    """
    # 删除物品（需要登录，只能删除自己的物品）
    return items_crud.delete_item(db=db, item_id=item_id, user_id=current_user.id)