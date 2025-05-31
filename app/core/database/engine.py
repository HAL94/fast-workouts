from sqlalchemy.ext.asyncio import create_async_engine

from app.core.database.url import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)