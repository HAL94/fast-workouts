from fastapi import APIRouter, Depends, Response

from app.api.v1.auth.service import AuthService, get_auth_service
from app.core.auth.jwt import validate_jwt
from app.core.auth.schema import UserRead, UserSigninRequest, UserSignupRequest
from app.core.common.app_response import AppResponse
from app.core.exceptions import UnauthorizedException


router = APIRouter(prefix="/auth")


@router.post("/login")
async def login(
    payload: UserSigninRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        data = await auth_service.login_user(payload)
        response.set_cookie(
            "ath", data.token, httponly=True, samesite="lax", max_age=60000
        )
        return AppResponse(data=data)
    except Exception as e:
        raise UnauthorizedException("Invalid credentials") from e


@router.get("/me")
async def get_user(user_data: UserRead = Depends(validate_jwt)):
    try:
        return AppResponse(data=user_data)
    except Exception as e:
        raise UnauthorizedException("Unauthorized") from e

@router.post("/signup")
async def signup(payload: UserSignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    data = await auth_service.sign_up_user(payload)
    if data is None:
        raise UnauthorizedException("Credentials invalid")
    return AppResponse(data=data, message="User created successfully", success=True)