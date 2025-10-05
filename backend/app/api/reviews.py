from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sqlalchemy.sql.functions import current_user

from .. import schemas, dependencies
from ..database import get_db
from ..crud import reviews as reviews_crud

# 创建路由实例
router = APIRouter()

# 创建评价
@router.post("/", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        创建评价（需要登录，只能评价已完成的交易）

        参数：
        - review: 评价信息（交易ID、被评价者ID、评分、评论等）

        返回：
        - 新创建的评价详情
    """
    return reviews_crud.create_review(
        db=db,
        review=review,
        reviewer_id=current_user.id
    )

# 获取用户收到的评价
@router.get("/user/{user_id}", response_model=List[schemas.ReviewResponse])
def read_user_reviews(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
        获取指定用户收到的评价（无需登录）

        参数：
        - user_id: 用户ID
        - skip: 跳过前n条记录（分页）
        - limit: 最多返回n条记录

        返回：
        - 评价列表
    """
    return reviews_crud.get_user_reviews(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

# 获取交易的评价
@router.get("/transaction/{transaction_id}", response_model=schemas.ReviewResponse)
def read_transaction_review(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
        获取指定交易的评价（需要登录，只能查看自己参与的交易的评价）

        参数：
        - transaction_id: 交易ID

        返回：
        - 评价详情
    """
    # 先获取交易，验证权限
    from ..crud.transactions import get_transaction
    transaction = get_transaction(db, transaction_id=transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="交易不存在")

    # 检查权限
    if transaction.buyer_id != current_user.id and transaction.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此交易的评价"
        )

    # 获取评价
    review = reviews_crud.get_transaction_review(db, transaction_id=transaction_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该交易尚未评价"
        )

    return review