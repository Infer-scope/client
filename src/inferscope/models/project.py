from typing import Union

from pydantic import BaseModel, ConfigDict, Field

from inferscope._utils import AutoStrEnum
from inferscope.models.find_filter import BaseFindFilter
from inferscope.models.interactive_base import InteractiveBaseModel
from inferscope.models.user import UserInfo


class Project(InteractiveBaseModel):
    class Status(AutoStrEnum):
        ACTIVE = "active"
        ARCHIVED = "archived"

    class CreateRequest(BaseModel):
        name: str = Field(min_length=1, max_length=255)
        description: Union[str, None] = None
        tags: Union[list[str], None] = None

    @classmethod
    def entity_name(cls) -> str:
        return "project"

    model_config = ConfigDict(extra="allow")
    status: Status
    owner: UserInfo
    members: list[UserInfo]
    name: str = Field(min_length=1, max_length=255)
    description: Union[str, None] = None
    tags: Union[list[str], None] = None


class ProjectFindFilter(BaseFindFilter):
    pass


class ProjectProperties(BaseModel):
    artifact_service_api_url: str
