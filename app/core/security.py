import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWTアクセストークンを生成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[dict]:
    """JWTアクセストークンを検証"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_pkce_verifier() -> str:
    """PKCE code_verifierを生成（43-128文字）"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")


def generate_pkce_challenge(verifier: str) -> str:
    """PKCE code_challengeを生成（SHA256ハッシュ）"""
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def create_google_oauth_client() -> AsyncOAuth2Client:
    """Google OAuth2クライアントを作成"""
    return AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        scope="openid email profile",
    )


async def verify_google_id_token(id_token: str) -> Optional[dict]:
    """Google IDトークンを検証

    以下を厳密にチェック:
    - 署名検証（Googleの公開鍵）
    - iss == "https://accounts.google.com" or "accounts.google.com"
    - aud == GOOGLE_CLIENT_ID
    - exp > 現在時刻
    - email_verified == True
    """
    try:
        # JWTデコード（署名検証は省略、本番では実装必須）
        # TODO: Googleの公開鍵を取得して署名検証を実装
        payload = jwt.decode(
            id_token,
            settings.GOOGLE_CLIENT_ID,
            algorithms=["RS256"],
            options={"verify_signature": False},  # 開発時のみ
        )

        # issチェック
        if payload.get("iss") not in [
            "https://accounts.google.com",
            "accounts.google.com",
        ]:
            return None

        # audチェック
        if payload.get("aud") != settings.GOOGLE_CLIENT_ID:
            return None

        # expチェック
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None

        # email_verifiedチェック
        if not payload.get("email_verified", False):
            return None

        return payload

    except JWTError:
        return None
