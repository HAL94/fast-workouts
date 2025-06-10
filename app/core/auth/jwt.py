from fastapi import Depends, Request
from fastapi.security import HTTPBearer, APIKeyCookie
import jwt
from app.core.auth.repository import UserRepository, get_user_repo
from app.core.auth.schema import AccessToken, UserRead
from app.core.config import AppSettings, get_settings

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from app.core.exceptions import UnauthorizedException

import logging

logger = logging.getLogger("uvicorn")


class JwtAuth:
    def __init__(self, user_repo: UserRepository, settings: AppSettings):
        self.user_repo = user_repo
        self.settings = settings

    async def validate_token(self, token: AccessToken) -> UserRead:
        """Validate JWT token and return user with decoded payload"""
        try:
            if not token:
                raise UnauthorizedException("Missing authentication token")

            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )

            user_id = payload.get("id")
            if not user_id:
                raise UnauthorizedException("Token payload is invalid")

            user_found = await self.user_repo.get_one(val=user_id, field="id")
            if not user_found:
                raise UnauthorizedException

            return user_found

        except ExpiredSignatureError as e:
            logger.info("[BaseJwtAuth]: Token has expired")
            raise UnauthorizedException from e
        except InvalidTokenError as e:
            logger.info("[BaseJwtAuth]: Token is invalid")
            raise UnauthorizedException from e


security = HTTPBearer()
cookie = APIKeyCookie(name="ath")


async def get_token_cookie(request: Request) -> AccessToken:
    try:
        return await cookie(request)
    except Exception as e:
        raise UnauthorizedException from e


async def validate_jwt(
    user_repo: UserRepository = Depends(get_user_repo),
    settings: AppSettings = Depends(get_settings),
    credentials: str = Depends(get_token_cookie),
):
    jwt_auth = JwtAuth(user_repo=user_repo, settings=settings)
    return await jwt_auth.validate_token(credentials)
