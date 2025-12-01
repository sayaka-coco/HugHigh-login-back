from fastapi import APIRouter, Depends
from app.api.deps import get_current_student
from app.models.user import User

router = APIRouter(prefix="/students", tags=["生徒機能"])


@router.get("/dashboard")
async def get_student_dashboard(current_user: User = Depends(get_current_student)):
    """
    生徒用ダッシュボード（サンプル）

    role=0 のユーザーのみアクセス可能
    """
    return {
        "message": "生徒用ダッシュボード",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "student_id": current_user.student_id,
            "class_name": current_user.class_name,
        },
    }
