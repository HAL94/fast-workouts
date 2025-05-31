

from fastapi import APIRouter


router = APIRouter(prefix="/auth")

@router.get("/me")
async def get_user():
    return {"message": "you logged in mate", "token": "some_str"}
