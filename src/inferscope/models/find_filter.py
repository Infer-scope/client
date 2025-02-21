from datetime import datetime
from typing import Union

from pydantic import BaseModel


class BaseFindFilter(BaseModel):
    limit: int = 100
    offset: int = 0
    created_lt: Union[datetime, None] = None
    created_gte: Union[datetime, None] = None
    tags: Union[list[str], None] = None
