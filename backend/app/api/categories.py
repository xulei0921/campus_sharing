from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .users import router
from .. import schemas, dependencies
from ..database import get_db
from ..crud import categories as categories_crud

# 创建路由实例
router = APIRouter()

# 创建分类
@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return categories_crud.create_category(db=db, category=category)

# 获取所有分类
@router.get("/", response_model=List[schemas.CategoryResponse])
def read_categories(
    skip: int = 0,  # 跳过前0条记录
    limit: int = 100,  # 最多返回100条记录
    db: Session = Depends(get_db)
):
    categories = categories_crud.get_categories(db, skip=skip, limit=limit)
    return categories

# 获取分类 by ID
@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    db_category = categories_crud.get_category(db, category_id=category_id)

    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")

    return db_category

# 更新分类
@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
        category_id: int,
        category: schemas.CategoryCreate,
        db: Session = Depends(get_db),
        current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return categories_crud.update_category(
        db=db,
        category_id=category_id,
        category_update=category
    )

# 删除分类
@router.delete("/{category_id}")
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return categories_crud.delete_category(db=db, category_id=category_id)