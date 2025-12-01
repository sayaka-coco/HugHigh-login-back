from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.auth_log import AuthLog


class AuthLogRepository:
    """認証ログリポジトリ"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: Optional[str],
        event_type: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_code: Optional[str] = None,
    ) -> AuthLog:
        """認証ログを作成"""
        auth_log = AuthLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            error_code=error_code,
        )
        self.db.add(auth_log)
        await self.db.commit()
        await self.db.refresh(auth_log)
        return auth_log
