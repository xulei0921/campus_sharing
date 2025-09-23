from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas

# 创建分类
def create_category(db: Session, category: schemas.CategoryCreate):
    # 检查分类名是否已存在
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类已存在"
        )

    # 创建分类对象
    db_category = models.Category(
        name=category.name,
        description=category.description
    )

    # 保存到数据库
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category

# 获取所有分类
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

# 获取分类 by ID
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

# 更新分类
def update_category(db: Session, category_id: int, category_update: schemas.CategoryCreate):
    db_category = get_category(db, category_id)

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    # 检查新分类名是否已被其他分类使用
    if category_update.name != db_category.name:
        existing_category = db.query(models.Category).filter(
            models.Category.name == category_update.name
        ).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类名已被使用"
            )

    # 更新字段
    db_category.name = category_update.name
    db_category.description = category_update.description

    db.commit()
    db.refresh(db_category)

    return db_category

# 删除分类
def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    # 检查该分类下是否有物品
    items_count = db.query(models.Item).filter(models.Item.category_id == category_id).count()
    if items_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下仍有物品，无法删除"
        )

    db.delete(db_category)
    db.commit()

    return {"message": "分类已成功删除"}