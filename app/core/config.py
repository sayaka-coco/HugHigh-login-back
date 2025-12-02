from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # データベース設定
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str
    SSL_CA_PATH: str = "./DigiCertGlobalRootG2.crt.pem"

    @property
    def database_url(self) -> str:
        """データベース接続URL"""
        return (
            f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?ssl_ca={self.SSL_CA_PATH}"
        )

    # JWT設定
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Google OAuth設定
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    @property
    def google_auth_endpoint(self) -> str:
        """Google認証エンドポイント"""
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def google_token_endpoint(self) -> str:
        """Googleトークンエンドポイント"""
        return "https://oauth2.googleapis.com/token"

    @property
    def google_userinfo_endpoint(self) -> str:
        """Googleユーザー情報エンドポイント"""
        return "https://www.googleapis.com/oauth2/v3/userinfo"

    # CORS設定
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """CORSオリジンのリスト"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Cookie設定
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str = "localhost"

    # 初期管理者設定
    INITIAL_ADMIN_EMAILS: str = ""

    @property
    def initial_admin_emails_list(self) -> List[str]:
        """初期管理者メールアドレスのリスト"""
        if not self.INITIAL_ADMIN_EMAILS:
            return []
        return [email.strip() for email in self.INITIAL_ADMIN_EMAILS.split(",")]


settings = Settings()
