from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class GoogleAuthURLResponse(BaseModel):
    """Google認証URLレスポンス"""

    auth_url: str


class TokenResponse(BaseModel):
    """トークンレスポンス"""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """トークンペイロード"""

    user_id: str
    role: int
    exp: int
    iat: int


class LoginResponse(BaseModel):
    """ログインレスポンス"""

    message: str
    redirect_url: str


class AuthLogResponse(BaseModel):
    """認証ログレスポンス"""

    id: str
    user_id: Optional[str]
    timestamp: datetime
    event_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    error_code: Optional[str]

    class Config:
        from_attributes = True


class AuthLogListResponse(BaseModel):
    """認証ログリストレスポンス"""

    logs: List[AuthLogResponse]
    total: int
