import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security

async def get_user_by_username(db:AsyncSession,username:str):
    stmt=select(User).where(User.username==username)
    result=await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession,user_data:UserRequest):
    hash_password=security.get_password_hash(user_data.password)
    user=User(username=user_data.username,password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_token(db:AsyncSession,user_id:int):
    token=str(uuid.uuid4())
    expire_at=datetime.now()+timedelta(days=7)
    query=select(UserToken).where(UserToken.user_id==user_id)
    result=await db.execute(query)
    user_token=result.scalar_one_or_none()
    if user_token:
        # 字段名是 expires_at(带 s), 与模型定义保持一致
        user_token.token=token
        user_token.expires_at=expire_at
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expire_at)
        db.add(user_token)
    # commit 提到分支外, 更新和新增都要提交
    await db.commit()
    return token

async def authenticate_user(db:AsyncSession,username:str,password:str):
    user=await get_user_by_username(db,username)
    if not user:
        raise HTTPException(status_code=400,detail="用户名或密码错误")
    if not security.verify_password(password,user.password):
        raise HTTPException(status_code=400,detail="用户名或密码错误")
    return user

async def get_user_by_token(db:AsyncSession,token:str):
    query=select(UserToken).where(UserToken.token==token)
    result=await db.execute(query)
    db_token=result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query=select(User).where(User.id==db_token.user_id)
    result=await db.execute(query)
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # ① 先确认用户存在（这一步就解决了"不存在"的判断）
    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # ② 取出要更新的字段
    update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        # 没有字段要改，直接返回当前数据
        return user

    # ③ 逐字段赋值
    for key, value in update_data.items():
        setattr(user, key, value)

    # ④ 提交
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(db: AsyncSession, user:User, old_password:str, new_password:str):
    if not security.verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    hashed_new_pwd = security.get_password_hash(new_password)
    user.password = hashed_new_pwd
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True