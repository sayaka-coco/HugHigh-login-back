from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


def generate_uuid():
    """UUID文字列を生成（ハイフンなし）"""
    return uuid.uuid4().hex


class User(Base):
    """ユーザーモデル（RFP準拠）"""

    __tablename__ = "users"

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Integer, nullable=False, index=True)  # 0:生徒, 1:教員, 2:管理者
    google_sub = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    student_id = Column(String(50), nullable=True)
    class_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
