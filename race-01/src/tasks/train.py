import flytekit as fl
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from src.core.model import xgb_classifier
from src.orchestration.constants import xgb_train_image

@fl.task(container_image=xgb_train_image)
def train_model(features: fl.FlyteFile) -> fl.FlyteFile:
    with open(features, "r", encoding="utf-8") as f:
        features = pd.read_csv(f)
    X = features.drop(columns=["acct", "label"])
    y = features["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    xgb_classifier.fit(X_train, y_train)

    y_pred = xgb_classifier.predict(X_test)
    print(classification_report(y_test, y_pred))

    features[["acct", "label"]].to_csv("acct_predict.csv", index=False)
    return fl.FlyteFile(path="acct_predict.csv")