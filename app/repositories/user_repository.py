from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.user import User


class UserRepository:
    """ユーザーリポジトリ"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """IDでユーザーを取得"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Google SubでユーザーをUser"""
        result = await self.db.execute(select(User).where(User.google_sub == google_sub))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """全ユーザーを取得"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def count(self) -> int:
        """ユーザー数をカウント"""
        result = await self.db.execute(select(User))
        return len(list(result.scalars().all()))

    async def create(self, user: User) -> User:
        """ユーザーを作成"""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """ユーザーを更新"""
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """ユーザーを削除"""
        await self.db.delete(user)
        await self.db.commit()
