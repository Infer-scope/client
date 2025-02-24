from typing import Union
from uuid import UUID

from inferscope.artifacts import StoredArtifactHelper
from inferscope.client import Client
from inferscope.models import DataDescription, ExternalLinkArtifact, StoredArtifact
from inferscope.models.data_description import DataFormatType, SemanticType, DataFormat
from inferscope.models.dataset import DatasetInfo
from inferscope.models.metric import Metric, MetricBestValue
from inferscope.models.model import ModelInfo
from inferscope.models.run import Run as RunModel, RunStatus


class Run:
    """A class to work with Run instance, adding artifacts to it and updating fields."""

    def __init__(self, client=None, uid: Union[UUID, None] = None, **kwargs):
        """Initialize a new Run instance.

        Args:
            client: Optional client instance for API communication. If None, creates a new Client with default user token from environment variable of from ~/.inferscope/token file.
            **kwargs: Run fields values, such as name, description, etc.
        """
        if client is None:
            self.client = Client()
        else:
            self.client = client

        if uid is None:
            self._model = RunModel(**kwargs)
        else:
            self._model = self.client.get(RunModel, uid)

        self.__artifact_pack_helper: Union[StoredArtifactHelper, None] = None

    def commit(self):
        """Commit the run and its artifacts to storage: if it's new run, create it, otherwise update it."""
        if self.__artifact_pack_helper is not None:
            self._model.artifact_pack_id = self.__artifact_pack_helper.pack_uid
        if self._model.uid is None:
            self._model = self.client.add(self._model)
        else:
            assert False, "We don't support run update with this interface for now"

    @property
    def _aph(self) -> StoredArtifactHelper:
        """Get or create a StoredArtifactHelper instance.

        Returns:
            StoredArtifactHelper: Helper instance for managing stored artifacts.
        """
        if self.__artifact_pack_helper is None:
            self.__artifact_pack_helper = StoredArtifactHelper(client=self.client)
        return self.__artifact_pack_helper

    def add_artifact(
        self,
        path,
        local_path=None,
        blob=None,
        uri=None,
        data_description: Union[DataDescription, None] = None,
    ) -> Union[StoredArtifact, ExternalLinkArtifact]:
        """Add an artifact to the run, either by uploading content or linking to external URI.

        Args:
            path: Path/name for the artifact.
            local_path: Optional local file path to upload.
            blob: Optional binary data to upload.
            uri: Optional external URI to link to.
            data_description: Optional metadata about the artifact's data format and semantics.

        Returns:
            StoredArtifact | ExternalLinkArtifact: The created artifact instance.

        Raises:
            AssertionError: If multiple source parameters (local_path, blob, uri) are provided.
        """
        if uri is None:
            return self._aph.upload_artifact(
                path=path,
                local_path=local_path,
                blob=blob,
                data_description=data_description,
            )
        else:
            assert (
                local_path is None and blob is None
            ), "Only one of local_path, blob or uri can be set"
            if not self._model.artifacts:
                self._model.artifacts = []
            ela = ExternalLinkArtifact(
                path=path, uri=uri, data_description=data_description
            )
            self._model.artifacts.append(ela)
            return ela

    def log_global_metric(
        self,
        name: str,
        value: Union[float, int, list[float], list[int]],
        slice: Union[str, None] = None,
        std: Union[float, None] = None,
        best_value: Union[MetricBestValue, None] = None,
    ):
        self._model.metrics.append(
            Metric(name=name, slice=slice, value=value, std=std, best_value=best_value)
        )

    def log_image(
        self,
        name: str,
        blob: Union[bytes, None] = None,
        local_path: Union[str, None] = None,
    ) -> str:
        """Log an image artifact to the run.

        Args:
            name: Name/path for the image artifact.
            blob: Optional binary image data.
            local_path: Optional path to local image file.

        Returns:
            str: URI of uploaded image. Typically starts with 'iss://', (InferScopeStorage protocol link)
        """
        return self.add_artifact(
            path=name,
            blob=blob,
            local_path=local_path,
            data_description=DataDescription(
                data_format=DataFormat(data_format=DataFormatType.Binary),
                semantic=SemanticType.Image,
            ),
        ).uri

    def log_video(
        self,
        name: str,
        blob: Union[bytes, None] = None,
        local_path: Union[str, None] = None,
    ) -> str:
        """Log video artifact to the run.

        Args:
            name: Name/path for the image artifact.
            blob: Optional binary image data.
            local_path: Optional path to local image file.

        Returns:
            str: URI of uploaded image. Typically starts with 'iss://', (InferScopeStorage protocol link)
        """
        return self.add_artifact(
            path=name,
            blob=blob,
            local_path=local_path,
            data_description=DataDescription(
                data_format=DataFormat(data_format=DataFormatType.Binary),
                semantic=SemanticType.Video,
            ),
        ).uri

    @property
    def metrics(self) -> list[Metric]:
        """Get the list of metrics logged to the run.

        Returns:
            list[Metric]: List of logged metrics.
        """
        return self._model.metrics

    @property
    def artifacts(self) -> list[Union[StoredArtifact, ExternalLinkArtifact]]:
        """Get the list of artifacts logged to the run.

        Returns:
            list[StoredArtifact | ExternalLinkArtifact]: List of logged artifacts.
        """
        return self._model.artifacts

    @property
    def name(self) -> str:
        """Get the name of the run.

        Returns:
            str: The name of the run.
        """
        return self._model.name

    @property
    def description(self) -> str:
        """Get the description of the run.

        Returns:
            str: The description of the run.
        """
        return self._model.description

    @property
    def status(self) -> RunStatus:
        """Get the status of the run.

        Returns:
            RunStatus: The status of the run.
        """
        return self._model.status

    @property
    def tags(self) -> list[str]:
        """Get the tags of the run."""
        return self._model.tags

    @property
    def dataset(self) -> DatasetInfo:
        """Get the dataset of the run."""
        return self._model.dataset

    @property
    def model(self) -> ModelInfo:
        """Get the model of the run."""
        return self._model.model

    @property
    def uid(self) -> UUID:
        """Get the uid of the run. Implicitly commits the run if it's not committed yet."""
        if not self._model.uid:
            self.commit()
        return self._model.uid

    @property
    def parent_project_uid(self) -> Union[UUID, None]:
        """Get the parent project uid of the run."""
        return self._model.parent_project_uid
