

from typing import Optional
from app.core.common.app_response import AppBaseModel


class CategoryBase(AppBaseModel):
    id: Optional[int] = None
    name: str