from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from .. import models, schemas
from .items import get_item, update_item  # 引入物品操作
from .users import update_credit_score  # 引入用户信用分操作

# 创建交易（发起交易请求）
def create_transaction(db: Session, transaction: schemas.TransactionCreate, buyer_id: int):
    # 买家发起交易请求
    # 检查物品是否存在
    item = get_item(db, item_id=transaction.item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    # 检查物品状态（必须是可交易状态）
    if item.status != schemas.ItemStatus.available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该物品当前不可交易"
        )

    # 检查不能购买自己的商品
    if item.user_id == buyer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能购买自己发布的物品"
        )

    # 检查是否已有未完成的交易
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.item_id == transaction.item_id,
        models.Transaction.status != schemas.TransactionStatus.cancelled,
        models.Transaction.status != schemas.TransactionStatus.completed
    ).first()

    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该物品已有未完成的交易"
        )

    # 创建交易对象
    db_transaction = models.Transaction(
        item_id=transaction.item_id,
        buyer_id=buyer_id,
        seller_id=item.user_id,
        meeting_time=transaction.meeting_time,
        meeting_location=transaction.meeting_location
    )

    # 保存交易
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # 更新物品状态为“交易中”
    update_item(
        db=db,
        item_id=item.id,
        item_update=schemas.ItemUpdate(status=schemas.ItemStatus.trading),
        user_id=item.user_id  # 卖家ID
    )

    return db_transaction

# 获取用户参与的交易（买家或卖家）
def get_user_transactions(
    db: Session,
    user_id: int,
    is_buyer: bool = True,
    status: Optional[schemas.TransactionStatus] = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(models.Transaction)

    # 筛选买家或卖家
    if is_buyer:
        query = query.filter(models.Transaction.buyer_id == user_id)
    else:
        query = query.filter(models.Transaction.seller_id == user_id)

    # 按状态筛选
    if status:
        query = query.filter(models.Transaction.status == status)

    # 按创建时间排序
    return query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()

# 获取交易详情
def get_transaction(db: Session, transaction_id: int):
    # 根据ID获取交易详情
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

# 更新交易状态
def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    user_id: int  # 当前操作的用户ID
):
    # 只有买家或卖家可以操作
    db_transaction = get_transaction(db, transaction_id=transaction_id)

    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )

    # 检查权限（必须是买家或卖家）
    if db_transaction.buyer_id != user_id and db_transaction.seller_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限操作此交易"
        )

    # 处理状态变更的业务逻辑
    current_status = db_transaction.status
    new_status = transaction_update.status

    if new_status:
        # 状态流转校验
        if new_status == schemas.TransactionStatus.confirmed:
            # 只有卖家可以确认交易
            if db_transaction.seller_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有卖家可以确认交易"
                )
            # 只能从pending状态变为confirmed
            if current_status != schemas.TransactionStatus.pending:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能确认待确认的交易"
                )

            elif new_status == schemas.TransactionStatus.completed:
                # 买家和卖家都可以标记交易完成
                # 只能从confirmed状态变为completed
                if current_status != schemas.TransactionStatus.confirmed:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="只能完成已确认的交易"
                    )

            elif new_status == schemas.TransactionStatus.cancelled:
                # 买家和卖家都可以取消交易
                # 不能取消已完成的交易
                if current_status == schemas.TransactionStatus.completed:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="已完成的交易不能取消"
                    )

    # 更新字段
    updata_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in updata_data.items():
        setattr(db_transaction, key, value)

    db.commit()
    db.refresh(db_transaction)

    # 如果交易取消，恢复物品为可交易状态
    if new_status == schemas.TransactionStatus.cancelled:
        update_item(
            db=db,
            item_id=db_transaction.item_id,
            item_update=schemas.ItemUpdate(status=schemas.ItemStatus.available),
            user_id=db_transaction.seller_id  # 卖家ID
        )

    # 如果交易完成，更新物品为已售出状态
    elif new_status == schemas.TransactionStatus.completed:
        update_item(
            db=db,
            item_id=db_transaction.item_id,
            item_update=schemas.ItemUpdate(status=schemas.ItemStatus.sold),
            user_id=db_transaction.seller_id  # 卖家ID
        )

    return db_transaction
