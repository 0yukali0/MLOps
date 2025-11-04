import flytekit as fl
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from src.core.model import xgb_classifier
from src.orchestration.constants import xgb_train_image


@fl.task(
    container_image=xgb_train_image,
    limits=fl.Resources(mem="5Gi", cpu="1", ephemeral_storage="10Gi"),
)
def train_model(feature_path: fl.FlyteFile) -> fl.FlyteFile:
    with open(feature_path, "r") as f:
        features = pd.read_csv(f)

    X = features[["acct_alert_recv", "acct_alert_send"]]
    y = features["account_type"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    xgb_classifier.fit(X_train, y_train)

    y_pred = xgb_classifier.predict(X_test)
    print(classification_report(y_test, y_pred))

    df_pred = features.copy()
    mask = df_pred["account_type"] != 1
    df_pred.loc[mask, "account_type"] = xgb_classifier.predict(
        df_pred.loc[mask, ["acct_alert_recv", "acct_alert_send"]]
    )

    # === 輸出結果 ===
    out = df_pred[["acct", "account_type"]].rename(columns={"account_type": "label"})
    out.to_csv("acct_predict.csv", index=False)
    return fl.FlyteFile(path="acct_predict.csv")
