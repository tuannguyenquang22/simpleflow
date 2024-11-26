from pydantic import BaseModel, Field
from typing import Dict
from . import model


class DataSourceCreate(BaseModel):
    name: str = Field(
        ...
    )
    origin: model.OriginType = Field(
        ...
    )
    connection_detail: Dict = Field(
        default_factory=dict
    )


class DataSourceUpdate(BaseModel):
    name: str = Field(
        ...
    )
    connection_detail: Dict = Field(
        default_factory=dict
    )