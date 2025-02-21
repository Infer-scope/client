from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import ConfigDict, Field

from inferscope._utils import AutoStrEnum
from inferscope.models.artifact import ExternalLinkArtifact, StoredArtifact
from inferscope.models.dataset import DatasetInfo
from inferscope.models.find_filter import BaseFindFilter
from inferscope.models.interactive_base import InteractiveBaseModel
from inferscope.models.metric import Metrics
from inferscope.models.model import ModelInfo


class RunStatus(AutoStrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    FAILED = "failed"
    DONE = "done"


class RunUpdateRequest(Metrics):
    name: Union[str, None] = Field(min_length=1, max_length=255, default=None)
    description: Union[str, None] = None
    status: Union[RunStatus, None] = None


class Run(InteractiveBaseModel, Metrics):
    class CreateRequest(Metrics):
        parent_project_uid: Union[UUID, None] = None

        name: Union[str, None] = Field(min_length=1, max_length=255, default=None)
        description: Union[str, None] = None
        dataset: Union[DatasetInfo, None] = None
        model: Union[ModelInfo, None] = None
        status: RunStatus = RunStatus.DONE
        tags: Union[list[str], None] = None
        artifact_pack_id: Union[UUID, None] = None
        artifacts: Union[list[ExternalLinkArtifact], None] = None

        override_datetime: Union[datetime, None] = None

    model_config = ConfigDict(extra="allow")

    @classmethod
    def entity_name(cls) -> str:
        return "run"

    access_ts: Union[datetime, None] = None
    parent_project_uid: Union[UUID, None] = None
    parent_experiment_uid: Union[UUID, None] = None

    name: Union[str, None] = Field(min_length=1, max_length=255, default=None)

    dataset: Union[DatasetInfo, None] = None
    description: Union[str, None] = None
    model: Union[ModelInfo, None] = None
    status: RunStatus = RunStatus.DONE
    tags: Union[list[str], None] = None

    artifact_pack_id: Union[UUID, None] = None
    artifacts: Union[list[Union[ExternalLinkArtifact, StoredArtifact]], None] = None


class RunFindFilter(BaseFindFilter):
    project_id: Union[str, None] = None
    experiment_id: Union[str, None] = None
