from typing import Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from inferscope._utils import AutoStrEnum
from inferscope.models.find_filter import BaseFindFilter
from inferscope.models.interactive_base import InteractiveBaseModel


class Experiment(InteractiveBaseModel):
    class Status(AutoStrEnum):
        DRAFT = "draft"
        ACTIVE = "active"
        FINISHED = "finished"
        FAILED = "failed"
        ARCHIVED = "archived"

    class CreateRequest(BaseModel):
        name: str = Field(min_length=1, max_length=255)
        parent_project: Union[UUID, None] = None
        description: Union[str, None] = None
        tags: Union[list[str], None] = None

    @classmethod
    def entity_name(cls) -> str:
        return "experiment"

    model_config = ConfigDict(extra="allow")
    parent_project: UUID
    status: Status
    name: str = Field(min_length=1, max_length=255)
    description: Union[str, None] = None
    tags: Union[list[str], None] = None


class ExperimentFindFilter(BaseFindFilter):
    project_list: Union[list[UUID], None] = None
