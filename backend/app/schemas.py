from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

# 物品状态枚举
class ItemStatus(str, Enum):
    available = "available"
    trading = "trading"
    sold = "sold"

# 交易状态枚举
class TransactionStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

# 用户模型 - 基础
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = None

# 用户模型 - 创建
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# 用户模型 - 更新
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

# 用户模型 - 响应
class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    credit_score: int
    created_at: datetime

    class Config:
        from_attributes = True  # 兼容SQLAlchemy模型

# 分类模型 - 基础
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=200)

# 分类模型 - 创建
class CategoryCreate(CategoryBase):
    pass

# 分类模型 - 响应
class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# 物品图片模型 - 基础
class ItemImageBase(BaseModel):
    image_url: str

# 物品图片模型 - 创建
class ItemImageCreate(ItemImageBase):
    pass

# 物品图片模型 - 响应
class ItemImageResponse(ItemImageBase):
    id: int
    item_id: int

    class Config:
        from_attributes = True

# 物品模型 - 基础
class ItemBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    location: Optional[str] = None

# 物品模型 - 创建
class ItemCreate(ItemBase):
    images: List[ItemImageCreate] = []

# 物品模型 - 更新
class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    status: Optional[ItemStatus] = None
    location: Optional[str] = None
    images: Optional[List[ItemImageCreate]] = []

# 物品模型 - 响应（简略）
class ItemBriefResponse(ItemBase):
    id: int
    status: ItemStatus
    user_id: int
    created_at: datetime
    owner: UserResponse
    images: List[ItemImageResponse] = []

    class Config:
        from_attributes = True

# 物品模型 - 响应（详细）
class ItemDetailResponse(ItemBriefResponse):
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

# 聊天模型 - 基础
class ChatBase(BaseModel):
    message: str

# 聊天模型 - 创建
class ChatCreate(ChatBase):
    item_id: int
    receiver_id: int

# 聊天模型 - 响应
class ChatResponse(ChatBase):
    id: int
    item_id: int
    sender_id: int
    receiver_id: int
    created_at: datetime
    sender: UserResponse

    class Config:
        from_attributes = True

# 交易模型 - 基础
class TransactionBase(BaseModel):
    meeting_time: Optional[datetime] = None
    meeting_location: Optional[str] = None

# 交易模型 - 创建
class TransactionCreate(TransactionBase):
    item_id: int

# 交易模型 - 更新
class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    meeting_time: Optional[datetime] = None
    meeting_location: Optional[str] = None

# 交易模型 - 响应
class TransactionResponse(TransactionBase):
    id: int
    item_id: int
    buyer_id: int
    seller_id: int
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    item: ItemBriefResponse
    buyer: UserResponse
    seller: UserResponse

    class Config:
        from_attributes = True

# 评价模型 - 基础
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5) # 1-5星
    comment: Optional[str] = None

# 评价模型 - 创建
class ReviewCreate(ReviewBase):
    transaction_id: int
    reviewee_id: int

# 评价模型 - 响应
class ReviewResponse(ReviewBase):
    id: int
    transaction_id: int
    reviewer_id: int
    reviewee_id: int
    created_at: datetime
    reviewer: UserResponse

    class Config:
        from_attributes = True

# 收藏模型 - 基础
class FavoriteBase(BaseModel):
    item_id: int

# 收藏模型 - 创建
class FavoriteCreate(FavoriteBase):
    pass

# 收藏模型 - 响应
class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    item: ItemBriefResponse

    class Config:
        from_attributes = True

# 登录请求
class LoginRequest(BaseModel):
    username: str
    password: str

# 令牌响应
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
