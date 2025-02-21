from typing import Literal, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from inferscope._utils import AutoStrEnum
from inferscope.models.data_description import DataDescription


class ArtifactType(AutoStrEnum):
    EXTERNAL_LINK = "external_link"
    STORED_ARTIFACT = "int_storage"


class BaseArtifact(BaseModel):
    path: str = Field(min_length=1, max_length=120)
    type: ArtifactType
    data_description: Union[DataDescription, None] = None


class ExternalLinkArtifact(BaseArtifact):
    type: Literal[ArtifactType.EXTERNAL_LINK] = ArtifactType.EXTERNAL_LINK
    uri: str


class StoredArtifact(BaseArtifact):
    type: Literal[ArtifactType.STORED_ARTIFACT] = ArtifactType.STORED_ARTIFACT
    uri: str
    direct_uri: Union[str, None] = None


class ArtifactInstance(BaseModel):
    name: str
    version: Union[str, None] = None
    description: Union[str, None] = None


class ArtifactPack(BaseModel):
    owner_project_uid: UUID
    artifacts: Union[List[Union[ExternalLinkArtifact, StoredArtifact]], None] = None
