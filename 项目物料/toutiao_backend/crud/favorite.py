from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News

async def is_news_favorite(db:AsyncSession,user_id:int,news_id:int):
    # 查的是 favorite 表(不是 news), 只取主键即可
    query=select(Favorite.id).where(Favorite.user_id==user_id,Favorite.news_id==news_id).limit(1)
    result=await db.execute(query)
    return result.scalar_one_or_none() is not None

async def add_news_favorite(db:AsyncSession,user_id:int,news_id:int):
    favorite=Favorite(user_id=user_id,news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
        db:AsyncSession,user_id:int,news_id:int):
    stmt=delete(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    await db.execute(stmt)
    await db.commit()
    return True

async def get_favorite_list(db:AsyncSession,user_id:int,page:int,page_size:int):
    # 查询 favorite 表, 关联 news 表, 取出 news 表的字段
    count_query=select(func.count()).where(Favorite.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one()
    offset=(page-1)*page_size
    query=select(News,Favorite.created_at.label('favorite_time'),Favorite.id.label('favorite_id')).join(
        Favorite,News.id==Favorite.news_id).where(
        Favorite.user_id==user_id).order_by(Favorite.created_at.desc()).offset(offset).limit(page_size)
    result=await db.execute(query)
    rows=result.all()
    return rows,total

async def remove_all_favorites(db:AsyncSession,user_id:int):
    stmt=delete(Favorite).where(Favorite.user_id==user_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
