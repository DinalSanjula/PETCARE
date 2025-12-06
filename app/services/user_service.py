from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.models.user_model import User
from app.schemas.user_schema import (UserCreate,UserReplace,UserPatch,UserResponse)
from app.auth.security import get_password_hash
from app.schemas.service_schema import (ServiceResponse,ServiceListResponse)


# CREATE USER
async def create_user(user: UserCreate, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        # Check email exists
        if await get_user_by_email(user.email, db):
            return ServiceResponse(success=False, message="User with this email already exists", data=None )

        hashed_pw = get_password_hash(user.password)

        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_pw,
            role=user.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return ServiceResponse(
            success=True,
            message="User created successfully",
            data=UserResponse.from_orm(db_user)
        )

    except Exception as e:
        await db.rollback()
        return ServiceResponse(
            success=False,
            message=f"Error creating user: {str(e)}",
            data=None
        )


# GET USER BY ID
async def get_user_by_id(user_id: int, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(
                success=False,
                message="User not found",
                data=None
            )

        return ServiceResponse(
            success=True,
            message="User retrieved successfully",
            data=UserResponse.from_orm(user)
        )

    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Error retrieving user: {str(e)}",
            data=None
        )


# GET USER BY EMAIL
async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# GET ALL USERS
async def get_all_users(limit: int, offset: int, db: AsyncSession) -> ServiceListResponse[UserResponse]:
    try:
        total = (await db.execute(select(func.count(User.id)))).scalar()

        users = (
            await db.execute(
                select(User).limit(limit).offset(offset)
            )
        ).scalars().all()

        user_list = [UserResponse.from_orm(u) for u in users]

        return ServiceListResponse(
            success=True,
            message="Users retrieved successfully",
            data=user_list,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        return ServiceListResponse(
            success=False,
            message=f"Error retrieving users: {str(e)}",
            data=[],
            total=0,
            limit=limit,
            offset=offset
        )


# UPDATE USER (PUT)
async def update_user(user_id: int, data: UserReplace, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(
                success=False,
                message="User not found",
                data=None
            )

        # Email conflict check
        if data.email != user.email:
            if await get_user_by_email(data.email, db):
                return ServiceResponse(
                    success=False,
                    message="Email already use",
                    data=None
                )

        user.name = data.name
        user.email = data.email
        user.age = data.age
        user.role = data.role
        user.password_hash = get_password_hash(data.password)

        await db.commit()
        await db.refresh(user)

        return ServiceResponse(
            success=True,
            message="User updated successfully",
            data=UserResponse.from_orm(user)
        )

    except Exception as e:
        await db.rollback()
        return ServiceResponse(
            success=False,
            message=f"Error updating user: {str(e)}",
            data=None
        )


# PATCH
async def patch_user(user_id: int, data: UserPatch, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(
                success=False,
                message="User not found",
                data=None
            )

        if data.name is not None:
            user.name = data.name

        if data.email is not None:
            if data.email != user.email:
                if await get_user_by_email(data.email, db):
                    return ServiceResponse(
                        success=False,
                        message="Email already use",
                        data=None
                    )
            user.email = data.email

        if data.age is not None:
            user.age = data.age

        if data.role is not None:
            user.role = data.role

        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        await db.commit()
        await db.refresh(user)

        return ServiceResponse(
            success=True,
            message="User updated successfully",
            data=UserResponse.from_orm(user)
        )

    except Exception as e:
        await db.rollback()
        return ServiceResponse(
            success=False,
            message=f"Error update user: {str(e)}",
            data=None
        )


# DELETE USEr
async def delete_user(user_id: int, db: AsyncSession) -> ServiceResponse[str]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(
                success=False,
                message="User not found",
                data=None
            )

        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()

        return ServiceResponse(success=True,message="User deleted successfully",data="deleted"
        )

    except Exception as e:
        await db.rollback()
        return ServiceResponse(success=False,message=f"Error deleting user: {str(e)}" , data=None
        )