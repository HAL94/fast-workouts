from typing import Optional
from pydantic import BaseModel

from app.core.common.app_response import AppBaseModel

type AccessToken = str


class UserRead(AppBaseModel):
    id: str | int
    full_name: Optional[str] = None
    email: str

class UserSignupData(BaseModel):
    email: str
    full_name: Optional[str] = None
    hashed_password: str

class UserReadWithPw(BaseModel):
    id: str | int
    full_name: Optional[str] = None
    email: str
    hashed_password: str


class UserData(AppBaseModel):
    user: UserRead
    token: AccessToken


class UserSignupRequest(AppBaseModel):
    email: str
    full_name: Optional[str] = None
    password: str


class UserSignupResponse(UserRead):
    pass


class UserSigninRequest(BaseModel):
    email: str
    password: str


class UserSigninResponse(UserData):
    pass
    