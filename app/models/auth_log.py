from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


def generate_uuid():
    """UUID文字列を生成（ハイフンなし）"""
    return uuid.uuid4().hex


class AuthLog(Base):
    """認証ログモデル（RFP準拠）"""

    __tablename__ = "auth_logs"

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    user_id = Column(
        CHAR(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    event_type = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<AuthLog(id={self.id}, event_type={self.event_type}, user_id={self.user_id})>"
