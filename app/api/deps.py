from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """現在のユーザーを取得（Cookieまたはヘッダーから）"""

    # 1. Cookieからトークンを取得
    token = request.cookies.get("access_token")

    # 2. Cookieにない場合はAuthorizationヘッダーから取得
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
        )

    # 3. トークン検証
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効です",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが無効です",
        )

    # 4. ユーザー取得
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    return user


def require_role(*allowed_roles: int):
    """
    権限チェックデコレータ

    使用例:
        require_role(0) -> 生徒のみ
        require_role(1, 2) -> 教員または管理者
        require_role(2) -> 管理者のみ
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="この操作を行う権限がありません",
            )
        return current_user

    return role_checker


# エイリアス
get_current_student = require_role(0)  # 生徒のみ
get_current_teacher = require_role(1, 2)  # 教員または管理者
get_current_admin = require_role(2)  # 管理者のみ
