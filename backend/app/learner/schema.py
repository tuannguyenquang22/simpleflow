from pydantic import BaseModel, Field
from typing import Optional, Dict
from .model import LearnerAlgo, LearnerTuning


class LearnerCreate(BaseModel):
    name: str = Field(
        ...,
    )
    description: Optional[str] = Field(
        default=None,
    )
    featureset_id: str = Field(
        ...,
    )
    problem_type: str = Field(
        ...,
    )
    test_size: Optional[float] = Field(
        default=0.2,
    )
    algorithm: LearnerAlgo = Field(
        ...,
    )
    schedule_condition: Optional[str] = Field(
        default=None,
    )
    tuning: Optional[LearnerTuning] = Field(
        default=None,
    )


class LearnerUpdate(BaseModel):
    name: str = Field(
        ...,
    )
    description: Optional[str] = Field(
        default=None,
    )
    featureset_id: str = Field(
        ...,
    )
    problem_type: str = Field(
        ...,
    )
    test_size: Optional[float] = Field(
        default=0.2,
    )
    algorithm: LearnerAlgo = Field(
        ...,
    )
    schedule_condition: Optional[str] = Field(
        default=None,
    )
    tuning: Optional[LearnerTuning] = Field(
        default=None,
    )