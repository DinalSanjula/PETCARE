from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserReplace, UserPatch, UserResponse
from app.auth.security import get_password_hash
from app.schemas.service_schema import ServiceResponse, ServiceListResponse, ServiceDeleteResponse


# Create user
async def create_user(user: UserCreate, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        #Check email exist
        if await get_user_by_email(user.email, db):
            return ServiceResponse(False, "User with this email already exists", None)

        #Create hashed password
        hashed_pw = get_password_hash(user.password)

        # Save user
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_pw,
            role=user.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return ServiceResponse(True,"User created successfully",UserResponse.from_orm(db_user)
        )

    except Exception as e:
        await db.rollback()
        return ServiceResponse(False, f"Error creating user: {str(e)}", None)


# GET USER BY ID
async def get_user_by_id(user_id: int, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(False, "User not found", None)

        return ServiceResponse(True, "User retrieved successfully", UserResponse.from_orm(user))

    except Exception as e:
        return ServiceResponse(False, f"Error retrieving user: {str(e)}", None)


# GET USER BY EMAIL
async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# GET ALL USERS (FAST & SAFE)
async def get_all_users(limit: int, offset: int, db: AsyncSession) -> ServiceListResponse[UserResponse]:
    try:
        # Count
        total = (await db.execute(select(func.count(User.id)))).scalar()

        # Fetch paginated users
        users = (await db.execute(
            select(User).limit(limit).offset(offset)
        )).scalars().all()

        user_list = [UserResponse.from_orm(u) for u in users]

        return ServiceListResponse(True, "Users retrieved successfully", user_list, total, limit, offset)

    except Exception as e:
        return ServiceListResponse(False, f"Error retrieving users: {str(e)}", [], 0, limit, offset)


# UPDATE USER (PUT)
async def update_user(user_id: int, data: UserReplace, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(False, "User not found", None)

        # Check email conflict
        if data.email != user.email:
            if await get_user_by_email(data.email, db):
                return ServiceResponse(False, "Email already in use", None)

        # Replace values
        user.name = data.name
        user.email = data.email
        user.age = data.age
        user.role = data.role
        user.password_hash = get_password_hash(data.password)

        await db.commit()
        await db.refresh(user)

        return ServiceResponse(True, "User updated successfully", UserResponse.from_orm(user))

    except Exception as e:
        await db.rollback()
        return ServiceResponse(False, f"Error updating user: {str(e)}", None)


# PATCH USER (PARTIAL UPDATE)
async def patch_user(user_id: int, data: UserPatch, db: AsyncSession) -> ServiceResponse[UserResponse]:
    try:
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(False, "User not found", None)

        # Conditional updates
        if data.name is not None:
            user.name = data.name

        if data.email is not None:
            if data.email != user.email:
                if await get_user_by_email(data.email, db):
                    return ServiceResponse(False, "Email already in use", None)
            user.email = data.email

        if data.age is not None:
            user.age = data.age

        if data.role is not None:
            user.role = data.role

        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        await db.commit()
        await db.refresh(user)

        return ServiceResponse(True, "User updated successfully", UserResponse.from_orm(user))

    except Exception as e:
        await db.rollback()
        return ServiceResponse(False, f"Error updating user: {str(e)}", None)


# DELETE USER
async def delete_user(user_id: int, db: AsyncSession) -> ServiceResponse[str]:
    try:
        user = await get_user_by_email(user_id, db)

        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user:
            return ServiceResponse(False, "User not found", None)

        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()

        return ServiceResponse(True, "User deleted successfully", "deleted")

    except Exception as e:
        await db.rollback()
        return ServiceResponse(False, f"Error deleting user: {str(e)}", None)