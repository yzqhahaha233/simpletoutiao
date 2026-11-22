from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News

async def add_news_history(db:AsyncSession,user_id:int,news_id:int):
    history=select(History).where(History.user_id==user_id,History.news_id==news_id)
    result=await db.execute(history)
    history_ex=result.scalar_one_or_none()
    if history_ex:
        history_ex.view_time=datetime.now()
        await db.commit()
        await db.refresh(history_ex)
        return history_ex
    history=History(user_id=user_id,news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def get_history_list(db:AsyncSession,user_id:int,page:int,page_size:int):
    count_query=select(func.count()).where(History.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one()
    offset=(page-1)*page_size
    # 查出 News + 收藏时间 + 历史记录ID(前端删除历史需要 history_id)
    query=(select(News,History.view_time.label('view_time'),History.id.label('history_id')).
           join(History,News.id==History.news_id).where(History.user_id==user_id).
           order_by(History.view_time.desc()).offset(offset).limit(page_size))
    result=await db.execute(query)
    rows=result.all()
    return rows,total

async def remove_history(db:AsyncSession,user_id:int,news_id:int):
    """按 (user_id, news_id) 删除浏览记录.
    (user_id, news_id) 唯一, 所以一条新闻对一个用户只会有一条历史.
    """
    stmt=delete(History).where(History.user_id==user_id,History.news_id==news_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount>0

async def remove_all_history(db:AsyncSession,user_id:int):
    stmt=delete(History).where(History.user_id==user_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0