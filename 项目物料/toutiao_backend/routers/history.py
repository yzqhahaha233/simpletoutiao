from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.base import NewsItemBase
from schemas.history import HistoryAddRequest, HistoryNewsItemResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post('/add')
async def add_news_history(data: HistoryAddRequest,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    result=await history.add_news_history(db,user.id,data.news_id)
    # 返回普通 dict, 不要把 ORM 对象直接交给 jsonable_encoder
    return success_response(message="添加历史记录成功", data={
        "id": result.id,
        "newsId": result.news_id,
        "viewTime": result.view_time.isoformat(),
    })

@router.get('/list')
async def get_news_history_list(page: int = Query(1, ge=1),
                                page_size: int = Query(10, ge=1, le=100, alias='pageSize'),
                                user: User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    rows,total=await history.get_history_list(db,user.id,page,page_size)
    # 用 Pydantic 模型构造, 避免直接用 ORM 对象的 __dict__(含 _sa_instance_state 无法序列化)
    history_list=[
        HistoryNewsItemResponse(
            **NewsItemBase.model_validate(news).model_dump(),
            history_id=history_id,
            view_time=view_time,
        )
        for news,view_time,history_id in rows
    ]
    has_more=total>page*page_size
    data=HistoryListResponse(list=history_list,total=total,has_more=has_more)
    return success_response(message="获取历史记录列表成功", data=data)

@router.delete('/delete/{news_id}')
async def remove_one_history(news_id:int,user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    # 按 news_id 删除当前用户对该新闻的浏览记录
    result=await history.remove_history(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="删除历史记录失败, 记录不存在")
    return success_response(message="删除历史记录成功")

@router.delete('/clear')
async def remove_all_history(user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    result=await history.remove_all_history(db,user.id)
    return success_response(message=f"清空了{result}条记录")
