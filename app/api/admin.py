from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["管理者機能"])


@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー一覧を取得（管理者のみ）
    """
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)
    total = await user_repo.count()

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーを作成（管理者のみ）

    必須項目:
    - email: Googleメールアドレス
    - role: 0(生徒), 1(教員), 2(管理者)

    任意項目:
    - name: 氏名
    - student_id: 学生番号
    - class_name: クラス
    """
    user_repo = UserRepository(db)

    # メールアドレス重複チェック
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # ユーザー作成
    new_user = User(
        email=user_data.email,
        role=user_data.role,
        name=user_data.name,
        student_id=user_data.student_id,
        class_name=user_data.class_name,
    )
    created_user = await user_repo.create(new_user)

    return UserResponse.model_validate(created_user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー詳細を取得（管理者のみ）
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー情報を更新（管理者のみ）

    注意: ユーザー本人は自分のロールを変更できません
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    # メールアドレス変更時の重複チェック
    if user_data.email and user_data.email != user.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています",
            )
        user.email = user_data.email

    # 更新
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.student_id is not None:
        user.student_id = user_data.student_id
    if user_data.class_name is not None:
        user.class_name = user_data.class_name

    updated_user = await user_repo.update(user)
    return UserResponse.model_validate(updated_user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーを削除（管理者のみ）
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    # 自分自身は削除できない
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自分自身を削除することはできません",
        )

    await user_repo.delete(user)
    return None
