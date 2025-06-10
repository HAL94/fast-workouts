from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.exceptions import AppException
from app.core.setup import create_application
from app.api import router as api_router

from sqlalchemy.sql import text
from app.dependencies.database import get_async_session

app = create_application(api_router=api_router, settings=settings)

logger = logging.getLogger("uvicorn")


@app.get("/welcome")
async def welcome():
    return {"success": True}


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check fail. Error message is: {str(e)}",
        )


def exception_handler(exc: Exception):
    if isinstance(exc, AppException):
        content = exc.dict()
    elif isinstance(exc, HTTPException):
        content = AppException(status_code=exc.status_code, message=exc.detail).dict()
    else:
        message = str(exc) if settings.ENV == "dev" else "Internal Server Error"
        content = AppException(status_code=500, message=message).dict()    
    return JSONResponse(content=content, status_code=content.get("status_code", 500))



@app.exception_handler(Exception)
async def global_exception_handler_by_generic_exception(
    request: Request, exc: Exception
):
    """Global exception handler for all unexpected errors"""
    logger.error(f"Method: {request.method}. Request Failed: URL: {request.url}.")
    return exception_handler(exc)


@app.exception_handler(StarletteHTTPException)
async def global_exception_handler(request: Request, exc: StarletteHTTPException):
    """Global exception handler for all http errors"""
    return exception_handler(exc)
