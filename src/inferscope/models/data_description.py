from enum import auto
from typing import Union

from pydantic import BaseModel, ConfigDict

from inferscope._utils import AutoStrEnum


class DataType(AutoStrEnum):
    Integer = auto()
    Float = auto()
    String = auto()
    Boolean = auto()
    Date = auto()

    URL = auto()  # string variant

    Bytes = auto()  # for inline image/audio


class SemanticType(AutoStrEnum):
    Prediction = auto()
    Metric = auto()

    Timestamp = auto()  # semantic for integer field

    JSON = auto()

    Image = auto()
    Audio = auto()
    Video = auto()
    Code = auto()
    Text = auto()

    Dataframe = auto()


class JoinType(AutoStrEnum):
    Inner = auto()


class ImageSematicProperties(BaseModel):
    _expected_sematic_type: SemanticType = SemanticType.Image
    preview_for_column: str


class MetricSemanticProperties(BaseModel):
    _expected_sematic_type: SemanticType = SemanticType.Metric
    diff_to_column: str


class ColumnInformation(BaseModel):
    name: str
    title: Union[str, None] = None
    tooltip: Union[str, None] = None
    type: DataType
    group_id: Union[str, None] = None
    show: bool = True
    semantic: Union[SemanticType, None] = None
    semantic_props: Union[
        ImageSematicProperties, MetricSemanticProperties, dict, None
    ] = None
    join_type: Union[JoinType, None] = None

    model_config = ConfigDict(extra="allow")


class DataFormatType(AutoStrEnum):
    JSON = auto()
    DSV = auto()
    Binary = auto()
    Pickle = auto()  # for insecure serialized formats


class DataFormat(BaseModel):
    data_format: DataFormatType
    dsv_delimiter: Union[str, None] = None  # for DSV

    model_config = ConfigDict(extra="allow")


class DataDescription(BaseModel):
    columns: Union[list[ColumnInformation], None] = (
        None  # Only applicable for Dataframe
    )
    data_format: DataFormat

    semantic: Union[SemanticType, None] = SemanticType.Dataframe

    model_config = ConfigDict(extra="allow")
