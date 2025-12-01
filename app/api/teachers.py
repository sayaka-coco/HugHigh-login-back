from fastapi import APIRouter, Depends
from app.api.deps import get_current_teacher
from app.models.user import User

router = APIRouter(prefix="/teachers", tags=["教員機能"])


@router.get("/dashboard")
async def get_teacher_dashboard(current_user: User = Depends(get_current_teacher)):
    """
    教員用ダッシュボード（サンプル）

    role=1 または role=2 のユーザーがアクセス可能
    """
    return {
        "message": "教員用ダッシュボード",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
        },
    }
