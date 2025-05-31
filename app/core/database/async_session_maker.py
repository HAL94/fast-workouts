from app.core.database.engine import engine
from sqlalchemy.ext.asyncio import async_sessionmaker

AsyncSessionMaker = async_sessionmaker(bind=engine, expire_on_commit=False)