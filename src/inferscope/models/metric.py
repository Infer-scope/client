from typing import Union

from pydantic import BaseModel, Field, ConfigDict

from inferscope._utils import AutoStrEnum


class MetricBestValue(AutoStrEnum):
    MIN = "min"
    MAX = "max"


class MetricType(AutoStrEnum):
    SCALAR = "scalar"
    SERIES = "series"
    TIME_SERIES = "time_series"


class MetricKeyParameters(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slice: Union[str, None] = None
    type: MetricType = MetricType.SCALAR
    best_value: Union[MetricBestValue, None] = None


class Metric(MetricKeyParameters):
    value: Union[float, int, list[float], list[int]]
    std: Union[float, None] = None


class Metrics(BaseModel):
    metrics: Union[list[Metric], None] = None
    model_config = ConfigDict(ser_json_inf_nan="strings")
