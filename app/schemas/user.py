from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""

    email: EmailStr
    role: int = Field(..., ge=0, le=2, description="0:生徒, 1:教員, 2:管理者")
    name: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None


class UserCreate(UserBase):
    """ユーザー作成スキーマ"""

    pass


class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""

    email: Optional[EmailStr] = None
    role: Optional[int] = Field(None, ge=0, le=2, description="0:生徒, 1:教員, 2:管理者")
    name: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None


class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""

    id: str
    google_sub: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""

    users: list[UserResponse]
    total: int
