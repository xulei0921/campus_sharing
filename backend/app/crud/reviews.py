from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from .. import models, schemas
from .transactions import get_transaction  # 引入交易操作
from .users import update_credit_score  # 引入用户信用分操作

# 创建评价
def create_review(db: Session, review: schemas.ReviewCreate, reviewer_id: int):
    """创建评价（交易完成后）"""
    # 检查交易是否存在
    transaction = get_transaction(db=db,transaction_id=review.transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )

    # 检查交易是否已完成
    if transaction.status != schemas.TransactionStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已完成的交易才能评价"
        )

    # 检查评价者是否是交易参与者
    if transaction.buyer_id != reviewer_id and transaction.seller_id != reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能评价自己参与的交易"
        )

    # 检查被评论者是否是交易的另一方
    if not (transaction.seller_id == review.reviewee_id or transaction.buyer_id == review.reviewee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="被评论者必须是交易的另一方"
        )

    # 检查不能评论自己
    if reviewer_id == review.reviewee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能评论自己"
        )

    # 检查交易是否已评价
    existing_review = db.query(models.Review).filter(
        models.Review.transaction_id == review.transaction_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该交易已评价，不能重复评价"
        )

    # 创建评价对象
    db_review = models.Review(
        transaction_id=review.transaction_id,
        reviewer_id=reviewer_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment
    )

    # 保存评价
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 根据评分调整被评价者的信用分
    # 5星+5分，4星+3分，3星不变，2星-3分，1星-5分
    score_change = 0
    if review.rating == 5:
        score_change = 5
    elif review.rating == 4:
        score_change = 3
    elif review.rating == 2:
        score_change = -3
    elif review.rating == 1:
        score_change = -5

    if score_change != 0:
        update_credit_score(db=db, user_id=review.reviewee_id, score_change=score_change)

    return db_review

# 获取用户收到的评价
def get_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取指定用户收到的评价"""
    return db.query(models.Review).filter(
        models.Review.reviewee_id == user_id
    ).order_by(models.Review.created_at.desc()).offset(skip).limit(limit).all()

# 获取交易的评价
def get_transaction_review(db: Session, transaction_id: int):
    """获取指定交易的评价"""
    return db.query(models.Review).filter(
        models.Review.transaction_id == transaction_id
    ).first()