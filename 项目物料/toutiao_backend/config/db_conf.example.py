"""
数据库配置示例文件

使用方法：
1. 把本文件复制一份，重命名为 db_conf.py
2. 把下面的 your_password 换成你自己的 MySQL 密码
3. db_conf.py 已在 .gitignore 中，不会被提交到 Git

为什么要这样做：
数据库密码属于敏感信息，不应该出现在公开仓库里。
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库URL —— 把 your_password 换成你的真实密码
ASYNC_DATABASE_URL = "mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选：输出SQL日志
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20  # 设置连接池允许创建的额外连接数
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
