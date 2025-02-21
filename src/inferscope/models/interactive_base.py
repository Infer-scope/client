from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field

from inferscope.models.user import UserInfo


class InteractiveBaseModel(BaseModel):
    uid: Union[UUID, None] = Field(init=False, default=None)
    created_by: Union[UserInfo, None] = Field(init=False, default=None)
    created_ts: Union[datetime, None] = Field(init=False, default=None)
    updated_ts: Union[datetime, None] = Field(init=False, default=None)
    access_ts: Union[datetime, None] = Field(init=False, default=None)

    @classmethod
    def entity_name(cls) -> str:
        pass

    @classmethod
    def entity_url(cls, entity_id: Union[str, UUID]) -> str:
        return f"{cls.entity_name()}/{entity_id}"

    @property
    def entity_create_url(self) -> str:
        return self.entity_name()

    def entity_delete_url(self) -> str:
        return self.entity_url(self.uid)

    @property
    def entity_search_url(self) -> str:
        return f"{self.entity_name()}s/"

    def make_create_request(self):
        return self.CreateRequest.model_validate(self)
