from typing import Optional, List
import aiomysql
from pydantic import EmailStr

from database import get_db_connection
from models import UserCreate, UserResponse, UserReplace, UserPatch
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


async def create_user(user: UserCreate) -> UserResponse:
    async with get_db_connection() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            #Check for duplicate email
            await cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            existing = await cursor.fetchone()
            if existing:
                raise Exception("Email already registered")

            #Hash password
            hashed_pw = hash_password(user.password)

            #Insert new user
            query = """
                INSERT INTO users (name, email, role, password)
                VALUES (%s, %s, %s, %s)
            """
            await cursor.execute(query, (user.name, user.email, user.role, hashed_pw))
            await conn.commit()  # commit changes
            user_id = cursor.lastrowid

            # Fetch and return created user
            await cursor.execute("SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = %s", (user_id,))
            result = await cursor.fetchone()

            return UserResponse(**result)


async def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    async with get_db_connection() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = %s"
            await cursor.execute(query, (user_id,))
            result = await cursor.fetchone()
            if result:
                return UserResponse(**result)
            return None

async def get_user_by_email(user_email : EmailStr):
    async with get_db_connection() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = %s"
            await cursor.execute(query , (user_email))
            result = await cursor.fetchone()
            if result :
                return UserResponse(**result)

async def get_all_user(limit: int, offset: int) -> List[UserResponse]:
    async with get_db_connection() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "SELECT id, name, email, role, created_at, updated_at FROM users ORDER BY id LIMIT %s OFFSET %s"
            await cursor.execute(query, (limit, offset))
            results = await cursor.fetchall()
            return [UserResponse(**r) for r in results]


async def delete_user(user_id: int):
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            query = "DELETE FROM users WHERE id = %s"
            await cursor.execute(query, (user_id,))
            await conn.commit()


async def update_user(user_id: int, user: UserReplace) -> Optional[UserResponse]:
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            # Hash password before update
            hashed_pw = hash_password(user.password)
            query = """
                UPDATE users 
                SET name = %s, email = %s, role = %s, password = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            await cursor.execute(query, (user.name, user.email, user.role, hashed_pw, user_id))
            await conn.commit()
    return await get_user_by_id(user_id)


async def patch_user(user_id: int, user: UserPatch) -> Optional[UserResponse]:
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            updates = []
            values = []

            if user.name is not None:
                updates.append("name = %s")
                values.append(user.name)
            if user.email is not None:
                updates.append("email = %s")
                values.append(user.email)
            if user.role is not None:
                updates.append("role = %s")
                values.append(user.role)
            if user.password is not None:
                updates.append("password = %s")
                values.append(hash_password(user.password))

            if not updates:
                return None

            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            await cursor.execute(query, tuple(values))
            await conn.commit()

        # Fetch updated record to return
        async with conn.cursor(aiomysql.DictCursor) as fetch_cursor:
            query = "SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = %s"
            await fetch_cursor.execute(query, (user_id,))
            result = await fetch_cursor.fetchone()
            if not result:
                return None
            return UserResponse(**result)