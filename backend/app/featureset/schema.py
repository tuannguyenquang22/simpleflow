from pydantic import BaseModel, Field
from typing import Optional, List


class ColumnMetadata(BaseModel):
    column: str = Field(
        ...,
    )
    data_type: str = Field(
        ...,
    )
    transformation: Optional[str] = Field(
        default="passthrough",
    )


class FeatureSetProfiling(BaseModel):
    datasource_id: str = Field(
        ...,
    )
    extract: Optional[str] = Field(
        default=None,
    )
    

class FeatureSetCreate(BaseModel):
    name: str = Field(
        ...,
    )
    datasource_id: str = Field(
        ...,
    )
    extract: Optional[str] = Field(
        default=None,
    )
    description: Optional[str] = Field(
        default=None,
    )
    features: List[ColumnMetadata] = Field(
        default_factory=list,
    )
    target: ColumnMetadata = Field(
        ...,
    )