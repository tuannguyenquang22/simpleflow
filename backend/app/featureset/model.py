from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, timezone
from .schema import ColumnMetadata

def get_current_datetime():
    return datetime.now(timezone.utc)


class FeatureSet(BaseModel):
    id: Optional[str] = Field(
        default=None,
        alias='_id'
    )
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
    modified: datetime = Field(
        default_factory=get_current_datetime,
    )
    features: List[ColumnMetadata] = Field(
        default_factory=list,
    )
    target: ColumnMetadata = Field(
        ...,
    )

    class Config:
        populate_by_name = True

    def model_dump(self, *args, **kwargs) -> Dict:
        return super().model_dump(*args, by_alias=True, exclude_none=True, **kwargs)
