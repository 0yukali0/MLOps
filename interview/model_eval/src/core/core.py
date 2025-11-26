# Core
import typing

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score


def compute_model_metric(df: pd.DataFrame) -> typing.Tuple[float, float, float, float]:
    df["y_true"] = df["Ground truth"].map({"Sick": 1, "No Sick": 0})
    df["y_pred"] = (df["AI pred"] >= 0.5).astype(int)
    accuracy = accuracy_score(df["y_true"], df["y_pred"])
    precision = precision_score(df["y_true"], df["y_pred"])
    recall = recall_score(df["y_true"], df["y_pred"])
    auc = roc_auc_score(df["y_true"], df["AI pred"])
    return accuracy, precision, recall, auc
