from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_google_oauth_client, verify_google_id_token, create_access_token
from app.repositories.user_repository import UserRepository
from app.repositories.auth_log_repository import AuthLogRepository
from app.models.user import User


class AuthService:
    """認証サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_log_repo = AuthLogRepository(db)

    async def get_google_auth_url(self) -> str:
        """Google認証URLを取得"""
        oauth_client = create_google_oauth_client()
        authorization_url, _ = oauth_client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            prompt="select_account",
        )
        return authorization_url

    async def login_with_google(
        self,
        code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Googleコードでログイン

        Returns:
            (user, access_token, error_code)
        """
        try:
            # 1. アクセストークン取得
            oauth_client = create_google_oauth_client()
            token = await oauth_client.fetch_token(
                "https://oauth2.googleapis.com/token",
                code=code,
            )

            if not token:
                await self.auth_log_repo.create(
                    user_id=None,
                    event_type="LOGIN_FAIL_TOKEN_EXCHANGE",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_code="TOKEN_EXCHANGE_FAILED",
                )
                return None, None, "TOKEN_EXCHANGE_FAILED"

            # 2. ユーザー情報取得
            user_info_response = await oauth_client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo"
            )
            user_info = user_info_response.json()

            email = user_info.get("email")
            google_sub = user_info.get("sub")
            email_verified = user_info.get("email_verified", False)

            # 3. email_verified チェック
            if not email_verified:
                await self.auth_log_repo.create(
                    user_id=None,
                    event_type="LOGIN_FAIL_EMAIL_NOT_VERIFIED",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_code="EMAIL_NOT_VERIFIED",
                )
                return None, None, "EMAIL_NOT_VERIFIED"

            # 4. DBでユーザー照合
            user = await self.user_repo.get_by_email(email)
            if not user:
                # 未登録ユーザー
                await self.auth_log_repo.create(
                    user_id=None,
                    event_type="LOGIN_FAIL_NOT_REGISTERED",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_code="USER_NOT_REGISTERED",
                )
                return None, None, "USER_NOT_REGISTERED"

            # 5. google_sub を保存（初回ログイン時）
            if not user.google_sub:
                user.google_sub = google_sub
                await self.user_repo.update(user)

            # 6. JWTトークン発行
            access_token = create_access_token(
                data={"user_id": user.id, "role": user.role}
            )

            # 7. ログイン成功ログ
            await self.auth_log_repo.create(
                user_id=user.id,
                event_type="LOGIN_SUCCESS",
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return user, access_token, None

        except Exception as e:
            # エラーログ
            await self.auth_log_repo.create(
                user_id=None,
                event_type="LOGIN_FAIL_OTHER",
                ip_address=ip_address,
                user_agent=user_agent,
                error_code=str(e)[:50],
            )
            return None, None, "UNKNOWN_ERROR"

    async def logout(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """ログアウト"""
        await self.auth_log_repo.create(
            user_id=user.id,
            event_type="LOGOUT",
            ip_address=ip_address,
            user_agent=user_agent,
        )
