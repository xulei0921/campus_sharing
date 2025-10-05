from sqlalchemy import false
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas
from ..utils import get_password_hash, verify_password

# 创建用户
def create_user(db: Session, user: schemas.UserCreate):
    """创建新用户"""
    # 检查用户名是否已存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户对象
    db_user = models.User(
        username = user.username,
        email = user.email,
        password = get_password_hash(user.password), # 存储加密后的密码
        phone = user.phone
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# 获取用户 by ID
def get_user(db: Session, user_id: int):
    """根据ID获取用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()

# 获取用户 by 用户名
def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()

# 验证用户（登录）
def authenticate_user(db: Session, username: str, password: str):
    """验证用户凭据"""
    user = get_user_by_username(db, username)

    if not user:
        return false()

    if not verify_password(password, user.password):
        return false()

    return user

# 更新用户信息
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """更新用户信息"""
    db_user = get_user(db, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user

# 更新用户信用分
def update_credit_score(db: Session, user_id: int, score_change: int):
    """更新用户信用分"""
    db_user = get_user(db, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新信用分，最低0分
    db_user.credit_score = max(0, db_user.credit_score + score_change)

    db.commit()
    db.refresh(db_user)

    return db_user