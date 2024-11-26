from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone
from enum import Enum


def get_current_datetime():
    return datetime.now(timezone.utc)


class OriginType(str, Enum):
    MYSQL = 'mysql'
    MONGODB = 'mongodb'
    MINIO = 'minio'


class DataSource(BaseModel):
    id: Optional[str] = Field(
        default=None,
        alias='_id'
    )
    name: str = Field(
        ...
    )
    description: Optional[str] = Field(
        default=None
    )
    origin: OriginType = Field(
        ...
    )
    modified: datetime = Field(
        default_factory=get_current_datetime
    )
    connection_detail: Dict = Field(
        default_factory=dict
    )

    class Config:
        populate_by_name = True

    def model_dump(self, *args, **kwargs) -> Dict:
        return super().model_dump(*args, by_alias=True, exclude_none=True, **kwargs)