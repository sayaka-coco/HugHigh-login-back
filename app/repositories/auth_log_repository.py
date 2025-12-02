from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List
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

    async def get_all(
        self, skip: int = 0, limit: int = 100, event_type: Optional[str] = None
    ) -> List[AuthLog]:
        """認証ログ一覧を取得"""
        query = select(AuthLog)
        if event_type:
            query = query.where(AuthLog.event_type == event_type)
        query = query.order_by(desc(AuthLog.timestamp)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, event_type: Optional[str] = None) -> int:
        """認証ログの総数を取得"""
        query = select(func.count(AuthLog.id))
        if event_type:
            query = query.where(AuthLog.event_type == event_type)
        result = await self.db.execute(query)
        return result.scalar() or 0
