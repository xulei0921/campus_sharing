from accelerate.commands.merge import description
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