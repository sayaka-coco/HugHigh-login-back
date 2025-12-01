from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 非同期エンジンの作成
engine = create_async_engine(
    settings.database_url,
    echo=True,  # 開発時はSQLログを出力
    pool_pre_ping=True,
    pool_recycle=3600,
)

# セッションファクトリ
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ベースクラス
Base = declarative_base()


async def get_db() -> AsyncSession:
    """データベースセッション依存性"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
