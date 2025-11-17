from fastapi import APIRouter ,status
from starlette.exceptions import HTTPException

import service
from models import UserCreate, UserReplace, UserPatch

router = APIRouter(prefix="/users")

@router.post("/" , status_code=status.HTTP_201_CREATED)
async def create_user(user:UserCreate):
    existing_user = await service.get_user_by_email(user.email)

    if existing_user :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exists")

    return await service.create_user(user)

@router.get("/email" , status_code=status.HTTP_404_NOT_FOUND)
async def get_user_by_email(email):
    return await service.get_user_by_email(email)

@router.get("/id/{id}")
async def get_user_by_id(id : int):
    return await service.get_user_by_id(id)

@router.get("/" , status_code=status.HTTP_200_OK)
async def get_all_users(limit : int = 10 , offset : int = 0):
    return await service.get_all_user(limit, offset)

@router.put("/{id}")
async def update_user(id : int , user: UserReplace):
    existing_user = await service.get_user_by_id(id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    await service.update_user(id, user)
    return {"info": "user updated successfully", "user": existing_user}

@router.patch("/{id}")
async def patch_user(id : int , user : UserPatch):
    existing_user = await service.get_user_by_id(id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    await service.patch_user(id, user)
    return {"info": "user patched successfully", "user": existing_user}

@router.delete("/{id}")
async def delete_user(id:int):
    existing_user = await service.get_user_by_id(id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="user not found")
    await service.delete_user(id)
    return {"info" : "user delected successfully" , "user" : existing_user}
