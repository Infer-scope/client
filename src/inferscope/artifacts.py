from dataclasses import dataclass
from typing import Union
from uuid import UUID

from inferscope.client import Client
from inferscope.models.data_description import DataDescription
from inferscope.models import ArtifactPack, StoredArtifact


@dataclass
class StoredArtifactHelper:
    _client: Client
    _pack_uid: UUID
    _parent_project_uid: UUID
    _artifact_package: Union[ArtifactPack, None] = None

    def __init__(self, client: Client, parent_project_uid: Union[UUID, None] = None):
        self._client = client
        self._parent_project_uid = (
            parent_project_uid
            if parent_project_uid is not None
            else client.get_default_project().uid
        )
        self._pack_uid = client.create_artifact_package(self._parent_project_uid)
        self._artifact_package = None

    def upload_artifact(
        self,
        path: str,
        blob: Union[bytes, str, None] = None,
        local_path: Union[str, None] = None,
        data_description: Union[DataDescription, None] = None,
    ) -> StoredArtifact:
        assert bool(blob) != bool(
            local_path
        ), "Exactly one parameter: blob or local_path can be specified"
        if local_path:
            blob = open(local_path, "rb").read()
        return self._client.upload_file_to_artifact_pack(
            parent_project_id=self._parent_project_uid,
            artifact_pack_id=self._pack_uid,
            path=path,
            blob=blob,
            data_description=data_description,
        )

    @property
    def pack_uid(self) -> UUID:
        return self._pack_uid
