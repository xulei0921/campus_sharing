from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, Enum, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

# 物品状态枚举
class ItemStatus(str, enum.Enum):
    available = "available"  # 可交易
    trading = "trading"      # 交易中
    sold = "sold"            # 已售出

# 交易状态枚举
class TransactionStatus(str, enum.Enum):
    pending = "pending"      # 待确认
    confirmed = "confirmed"  # 已确认
    completed = "completed"  # 已完成
    cancelled = "cancelled"  # 已取消

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)  # 存储加密后的密码
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    credit_score = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：用户发布的物品
    items = relationship("Item", back_populates="owner")
    # 关系：用户的聊天消息（作为发送者）
    sent_messages = relationship("Chat", foreign_keys="Chat.sender_id", back_populates="sender")
    # 关系：用户收到的聊天消息
    received_messages = relationship("Chat", foreign_keys="Chat.receiver_id", back_populates="receiver")
    # 关系：用户作为买家的交易
    buyer_transactions = relationship("Transaction", foreign_keys="Transaction.buyer_id", back_populates="buyer")
    # 关系：用户作为卖家的交易
    seller_transactions = relationship("Transaction", foreign_keys="Transaction.seller_id", back_populates="seller")
    # 关系：用户的收藏
    favorites = relationship("Favorite", back_populates="user")

# 分类模型
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)

    # 关系：该分类下的物品
    items = relationship("Item", back_populates="category")

# 物品模型
class Item(Base):
    __tablename__="items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10,2), nullable=True)  # 可为null表示免费
    status = Column(Enum(ItemStatus), default=ItemStatus.available)
    location = Column(String(100), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：物品所属分类
    category = relationship("Category", back_populates="items")
    # 关系：物品的所有者
    owner = relationship("User", back_populates="items")
    # 关系：物品的图片
    images = relationship("ItemImage", back_populates="item", cascade="all, delete-orphan")
    # 关系：关于该物品的聊天
    chats = relationship("Chat", back_populates="item")
    # 关系：该物品的交易
    transactions = relationship("Transaction", back_populates="item")
    # 关系：收藏该物品的用户
    favorites = relationship("Favorite", back_populates="item")

# 物品图片模型
class ItemImage(Base):
    __tablename__ = "item_images"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    image_url = Column(String(255), nullable=False)

    # 关系：图片所属物品
    item = relationship("Item", back_populates="images")

# 聊天模型
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系：聊天所属物品
    item = relationship("Item", back_populates="chats")
    # 关系：发送者
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    # 关系：接收者
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

# 交易模型
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending)
    meeting_time = Column(DateTime, nullable=True)
    meeting_location = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：交易涉及的物品
    item = relationship("Item", back_populates="transactions")
    # 关系：买家
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="buyer_transactions")
    # 关系：卖家
    seller = relationship("User", foreign_keys=[seller_id], back_populates="seller_transactions")
    # 关系：交易的评价
    review = relationship("Review", back_populates="transaction", uselist=False)

# 评价模型
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewee_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)  # 1-5星
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系：评价所属交易
    transaction = relationship("Transaction", back_populates="review")

# 收藏模型
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系：收藏的用户
    user = relationship("User", back_populates="favorites")
    # 关系：被收藏的物品
    item = relationship("Item", back_populates="favorites")