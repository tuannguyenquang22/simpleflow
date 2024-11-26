from typing import Optional
from sklearn.metrics import accuracy_score, root_mean_squared_error, log_loss, f1_score, precision_score, recall_score, \
    roc_auc_score, mean_absolute_error
from sklearn.ensemble import StackingClassifier, StackingRegressor
from sklearn.model_selection import train_test_split
from worker.database import MINIO_CLIENT
from worker.model import get_model
from app.learner.model import LearnerAlgo, LearnerTuning
from ray import tune
from ray.tune.search.hyperopt import HyperOptSearch
from .celery_app import celery_app
import os
import pandas as pd


def read_feature_set(bucket_name: str, object_name: str):
    try:
        data = MINIO_CLIENT.get_object(bucket_name, object_name)
        with open("temp.csv", "wb") as file:
            for chunk in data.stream(32 * 1024):
                if chunk:
                    file.write(chunk)
    except Exception:
        raise Exception(f"Failed to read data from {bucket_name}/{object_name}")


@celery_app.task(name="tasks.execute_training")
def execute_training(
    self,
    learner_id: str,
    bucket_name: str,
    object_name: str,
    target_column: str,
    problem_type: str,
    algorithm: LearnerAlgo,
    test_size: float,
    tuning: Optional[LearnerTuning] = None,
):
    self.update_state(state="STARTED", meta={"learner_id": learner_id})
    try:
    # Load feature set from MinIO
        read_feature_set(bucket_name, object_name)
        df = pd.read_csv("temp.csv")
        os.remove("temp.csv")
    except Exception:
        return {"error": "Failed to read data from MinIO"}

        # Split data into X and y
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = None

    # Get model
    model_name = algorithm.name
    if model_name != "stacking":
        model = get_model(problem_type, model_name)
    else:
        estimators = list()
        for b in algorithm.base_learners:
            b_name = b.name
            b_model = get_model(problem_type, b_name)
            if b.params:
                b_model.set_params(**b.params)
            estimators.append((b_name, b_model))

        m = algorithm.meta_learner
        m_name = m.name
        m_model = get_model(problem_type, m_name)
        if m.params:
            m_model.set_params(**m.params)

        meta_estimator = m_model
        model = StackingClassifier(estimators=estimators, final_estimator=meta_estimator) \
            if problem_type == "classification" \
            else StackingRegressor(estimators=estimators, final_estimator=meta_estimator)


    if tuning:
        objective_metric = tuning.metric
        objective_direction = tuning.direction
        max_trials = tuning.max_trials

        config = {}
        for item in tuning.search_space:
            if isinstance(item.values, list):
                config.update({item.name: tune.choice(item.values)})
            elif isinstance(item.values, tuple):
                data_type = item.data_type
                if data_type == "int":
                    config.update({item.name: tune.randint(item.values[0], item.values[1])})
                elif data_type == "float":
                     config.update({item.name: tune.uniform(item.values[0], item.values[1])})

        def fitness(config):
            model.set_params(**config)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            if objective_metric == "accuracy":
                score = accuracy_score(y_test, y_pred)
            elif objective_metric == "rmse":
                score = root_mean_squared_error(y_test, y_pred)
            elif objective_metric == "r2":
                score = model.score(X_test, y_test)
            elif objective_metric == "mae":
                score = mean_absolute_error(y_test, y_pred)
            elif objective_metric == "log_loss":
                score = log_loss(y_test, y_pred)
            elif objective_metric == "f1":
                score = f1_score(y_test, y_pred)
            elif objective_metric == "precision":
                score = precision_score(y_test, y_pred)
            elif objective_metric == "recall":
                score = recall_score(y_test, y_pred)
            elif objective_metric == "roc_auc":
                score = roc_auc_score(y_test, y_pred)
            else:
                raise ValueError(f"Invalid objective metric: {objective_metric}")
                
            return {"score": score}
            
        algo = HyperOptSearch()
        tuner = tune.Tuner(
            fitness,
            tune_config=tune.TuneConfig(
                metric="score",
                mode=objective_direction,
                search_alg=algo,
                num_samples=max_trials,
            ),
            param_space=config,
        )
        result = tuner.fit()
        return {"best_config": result.get_best_result().config, "best_score": result.get_best_result().metrics["score"]}

    if model is None:
        return {"error": "Failed to get model"}

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    score = {}

    if problem_type == "classification":
        score = {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred),
            "log_loss": log_loss(y_test, y_pred),
        }
    elif problem_type == "regression":
        score = {
            "rmse": root_mean_squared_error(y_test, y_pred),
            "r2": model.score(X_test, y_test),
            "mae": mean_absolute_error(y_test, y_pred),
        }

    return {"score": score}
