from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.schemas.auth import GoogleAuthURLResponse, LoginResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["認証"])


def _get_client_info(request: Request) -> tuple[str, str]:
    """クライアント情報を取得"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


def _set_access_token_cookie(response: Response, access_token: str) -> None:
    """アクセストークンをCookieにセット"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN != "localhost" else None,
    )


def _clear_access_token_cookie(response: Response) -> None:
    """アクセストークンCookieをクリア"""
    response.delete_cookie(
        key="access_token",
        domain=settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN != "localhost" else None,
    )


@router.get("/google/login", response_model=GoogleAuthURLResponse)
async def google_login(db: AsyncSession = Depends(get_db)):
    """
    Google認証URLを取得

    フロントエンドはこのURLにユーザーをリダイレクトします。
    """
    auth_service = AuthService(db)
    auth_url = await auth_service.get_google_auth_url()
    return GoogleAuthURLResponse(auth_url=auth_url)


@router.get("/google/callback", response_model=LoginResponse)
async def google_callback(
    code: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Google認証コールバック

    Googleから認証コードを受け取り、ユーザー情報を取得してログイン処理を行います。
    """
    ip_address, user_agent = _get_client_info(request)
    auth_service = AuthService(db)

    user, access_token, error_code = await auth_service.login_with_google(
        code=code,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if error_code:
        # エラーメッセージをシンプルに
        error_messages = {
            "USER_NOT_REGISTERED": "ログインに失敗しました。管理者にお問い合わせください。",
            "EMAIL_NOT_VERIFIED": "ログインに失敗しました。メールアドレスが未確認です。",
            "TOKEN_EXCHANGE_FAILED": "ログインに失敗しました。",
            "UNKNOWN_ERROR": "ログインに失敗しました。",
        }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_messages.get(error_code, "ログインに失敗しました。"),
        )

    # Cookieにアクセストークンをセット
    _set_access_token_cookie(response, access_token)

    # ロールに応じたリダイレクト先を決定
    redirect_map = {
        0: f"{settings.cors_origins_list[0]}/students",  # 生徒
        1: f"{settings.cors_origins_list[0]}/teachers",  # 教員
        2: f"{settings.cors_origins_list[0]}/admin",     # 管理者
    }
    redirect_url = redirect_map.get(user.role, settings.cors_origins_list[0])

    return LoginResponse(
        message="ログインに成功しました",
        redirect_url=redirect_url,
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ログアウト

    アクセストークンを無効化し、Cookieをクリアします。
    """
    ip_address, user_agent = _get_client_info(request)
    auth_service = AuthService(db)

    await auth_service.logout(
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Cookieをクリア
    _clear_access_token_cookie(response)

    return {"message": "ログアウトしました"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    現在のユーザー情報を取得
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "name": current_user.name,
        "student_id": current_user.student_id,
        "class_name": current_user.class_name,
    }
