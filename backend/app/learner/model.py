from typing import Optional, Dict, Union, List, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class LearnerMetric(str, Enum):
    accuracy = 'accuracy'
    f1 = 'f1'
    precision = 'precision'
    recall = 'recall'
    roc_auc = 'roc_auc'
    log_loss = 'log_loss'
    mae = 'mae'
    mse = 'mse'
    rmse = 'rmse'
    r2 = 'r2'


class LearnerSearchSpace(BaseModel):
    name: LearnerMetric = Field(
        ...,
    )
    data_type: str = Field(
        ...,
    )
    values: Union[List[str], Tuple[int, int]] = Field(
        ...,
    )


class LearnerTuning(BaseModel):
    metric: LearnerMetric = Field(
        ...,
    )
    direction: str = Field(
        ...,
    )
    search_space: List[LearnerSearchSpace] = Field(
        default_factory=list,
    )
    max_trials: int = Field(
        default=10,
    )


class LearnerBaseStacking(BaseModel):
    name: str = Field(
        ...,
    )
    params: Optional[Dict] = Field(
        default_factory=dict,
    )


class LearnerAlgo(BaseModel):
    name: str = Field(
        ...,
    )
    params: Optional[Dict] = Field(
        default_factory=dict,
    )
    base_learners: Optional[List[LearnerBaseStacking]] = Field(
        default_factory=list,
    )
    meta_learner: Optional[LearnerBaseStacking] = Field(
        default=None,
    )


class Learner(BaseModel):
    id: Optional[str] = Field(
        default=None,
        alias='_id'
    )
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
    tuning: Optional[LearnerTuning] = Field(
        default=None,
    )
    algorithm: LearnerAlgo = Field(
        ...,
    )
    schedule_condition: Optional[str] = Field(
        default=None,
    )

    class Config:
        populate_by_name = True

    def model_dump(self, *args, **kwargs) -> Dict:
        return super().model_dump(*args, by_alias=True, exclude_none=True, **kwargs)
