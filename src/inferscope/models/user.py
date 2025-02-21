from typing import Union

import pydantic


class UserInfo(pydantic.BaseModel):
    username: str
    avatar_url: Union[str, None] = None


class BackendUserInfo(pydantic.BaseModel):
    config: dict[str, object]
