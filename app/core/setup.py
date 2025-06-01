from contextlib import _AsyncGeneratorContextManager, asynccontextmanager

from typing import Any, AsyncGenerator, Callable


from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import AppSettings
from app.core.database import engine


def lifespan_factory(settings: AppSettings) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        yield
        await engine.dispose()

    return lifespan


def add_cors_middleware(app: FastAPI) -> FastAPI:
    app.add_middleware(CORSMiddleware,
                       allow_origins=["http://localhost:3000"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])
    return app


def create_application(api_router: APIRouter, settings: AppSettings, **kwargs) -> FastAPI:
    lifespan = lifespan_factory(settings)

    app = FastAPI(lifespan=lifespan, **kwargs)

    app.include_router(api_router)
    app = add_cors_middleware(app)

    return app
