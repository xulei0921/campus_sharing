from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, dependencies
from ..database import get_db
from ..crud import transactions as transactions_crud

# 创建路由实例
router = APIRouter()

# 创建交易（发起交易请求）
@router.post("/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        发起交易请求（买家操作，需要登录）

        参数：
        - transaction: 交易信息（物品ID、交易时间、地点等）

        返回：
        - 新创建的交易详情
    """
    # 发起交易请求（买家操作，需要登录）
    return transactions_crud.create_transaction(
        db=db,
        transaction=transaction,
        buyer_id=current_user.id
    )

# 获取用户作为买家的交易
@router.get("/my-buy", response_model=List[schemas.TransactionResponse])
def read_my_buy_transactions(
    status: Optional[schemas.TransactionStatus] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取当前用户作为买家的交易（需要登录）

        参数：
        - status: 按交易状态筛选
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录

        返回：
        - 交易列表
    """
    # 获取当前用户作为买家的交易（需要登录）
    return transactions_crud.get_user_transactions(
        db,
        user_id=current_user.id,
        is_buyer=True,
        status=status,
        skip=skip,
        limit=limit
    )

# 获取用户作为卖家的交易
@router.get("/my-sell", response_model=List[schemas.TransactionResponse])
def read_my_seller_transactions(
    status: Optional[schemas.TransactionStatus] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取当前用户作为卖家的交易（需要登录）

        参数：
        - status: 按交易状态筛选
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录

        返回：
        - 交易列表
    """
    # 获取当前用户作为卖家的交易（需要登录）
    return transactions_crud.get_user_transactions(
        db,
        user_id=current_user.id,
        is_buyer=False,
        status=status,
        skip=skip,
        limit=limit
    )

# 获取交易详情
@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取交易详情（需要登录，只能查看自己参与的交易）

        参数：
        - transaction_id: 交易ID

        返回：
        - 交易详细信息
    """
    # 获取交易详情（需要登录，只能查看自己参与的交易）
    db_transaction = transactions_crud.get_transaction(db, transaction_id=transaction_id)

    if not db_transaction:
        raise HTTPException(
            status_code=404,
            detail="交易不存在"
        )

    # 检查权限（只能查看自己参与的交易）
    if db_transaction.buyer_id != current_user.id and db_transaction.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此交易"
        )

    return db_transaction

# 更新交易（主要用于更新状态）
@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        更新交易信息（需要登录，只能操作自己参与的交易）

        参数：
        - transaction_id: 交易ID
        - transaction: 要更新的交易信息（状态、时间、地点等）

        返回：
        - 更新后的交易信息
    """
    # 更新交易信息（需要登录，只能操作自己参与的交易）
    return transactions_crud.update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction_update=transaction,
        user_id=current_user.id
    )