from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional

from .. import models, schemas

# 创建物品
def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
    # 创建物品对象
    db_item = models.Item(
        title=item.title,
        description=item.description,
        price=item.price,
        category_id=item.category_id,
        location=item.location,
        user_id=user_id
    )

    # 保存物品
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 添加物品图片
    if item.images:
        for image in item.images:
            db_item = models.ItemImage(
                item_id=db_item.id,
                image_url=image.image_url
            )
            db.add(db_item)
        db.commit()
        # 刷新物品信息以包含图片
        db.refresh(db_item)
    return db_item

# 获取物品列表（支持筛选）
def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[schemas.ItemStatus] = None
):
    query = db.query(models.Item)

    # 按分类筛选
    if category_id:
        query = query.filter(models.Item.category_id == category_id)

    # 按关键词搜索（标题或描述）
    if search:
        query = query.filter(
            or_(
                models.Item.title.contains(search),
                models.Item.description.contains(search)
            )
        )

    # 按价格范围筛选
    if min_price is not None:
        query = query.filter(models.Item.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Item.price <= max_price)

    # 按状态筛选
    if status:
        query = query.filter(models.Item.status == status)

    # 执行查询（按创建时间倒序，最新的在前面）
    return query.order_by(models.Item.created_at.desc()).offset(skip).limit(limit).all()

# 获取用户发布的物品
def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.Item).filter(
        models.Item.user_id == user_id
    ).order_by(models.Item.created_at.desc()).offset(skip).limit(limit).all()

# 获取物品 by ID
def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

# 更新物品
def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate, user_id: int):
    db_item = get_item(db, item_id)

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查权限（只能更新自己的物品）
    if db_item.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此物品"
        )

    # 更新字段
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)

    return db_item

# 删除物品
def delete_item(db: Session, item_id: int, user_id: int):
    db_item = get_item(db, item_id)

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查权限
    if db_item.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此物品"
        )

    # 检查物品状态（只有可交易状态才能删除）
    if db_item.status != schemas.ItemStatus.available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有可交易状态的物品才能删除"
        )

    db.delete(db_item)
    db.commit()

    return {"message": "物品已成功删除"}