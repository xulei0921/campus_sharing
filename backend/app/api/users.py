from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import schemas, dependencies
from ..database import get_db
from ..crud import users as users_crud
from ..utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

# 创建路由实例
router = APIRouter()

# 用户注册
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_crud.create_user(db=db,user=user)

# 用户登录
@router.post("/login", response_model=schemas.TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 验证用户
    user = users_crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# 获取当前用户信息
@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return current_user

# 更新当前用户信息
@router.put("/me", response_model=schemas.UserResponse)
def update_current_user(
        user_update: schemas.UserUpdate,
        current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
        db: Session = Depends(get_db)
):
    return users_crud.update_user(db=db, user_id=current_user.id, user_update=user_update)

# 获取用户 by ID
@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    db_user = users_crud.get_user(db,user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return db_user