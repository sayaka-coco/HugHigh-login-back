from pydantic import BaseModel
from typing import Optional


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
