import flytekit as fl
import pandas as pd
from src.orchestration.constants import eda_image

@fl.task(container_image=eda_image, cache=fl.Cache(version="1.0", serialize=True), limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"))
def accounts(transaction_path: str = "s3://data/accounts/acct_transaction.csv") -> fl.FlyteFile:
    transaction_file = fl.FlyteFile.from_source(transaction_path)
    with open(transaction_file, "r") as f:
        txn = pd.read_csv(f)
    from_df = (
        df.loc[df["from_acct_type"] == 1, ["from_acct"]]
        .drop_duplicates()
        .rename(columns={"from_acct": "acct"})
    )

    to_df = (
        df.loc[df["to_acct_type"] == 1, ["to_acct"]]
        .drop_duplicates()
        .rename(columns={"to_acct": "acct"})
    )

    acct_df = pd.concat([from_df, to_df]).drop_duplicates(subset=["acct"])
    acct_df.to_csv("unique_acct.csv", index=False)
    return fl.FlyteFile(path="unique_acct.csv")


@fl.task(container_image=eda_image, cache=fl.Cache(version="1.0", serialize=True), limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"))
def eda(
        transaction_path: str = "s3://data/accounts/acct_transaction.csv",
        alert_path: str = "s3://data/accounts/acct_alert.csv",
    ) -> fl.FlyteFile:
    transaction_file = fl.FlyteFile.from_source(transaction_path)
    with open(transaction_file, "r") as f:
        txn = pd.read_csv(f)
    # --- EDA ---
    from_features = txn.groupby("from_acct").agg(
        from_txn_count=("txn_amt", "count"),
        from_txn_sum=("txn_amt", "sum"),
        from_txn_mean=("txn_amt", "mean"),
        from_unique_to=("to_acct", "nunique"),
    ).reset_index().rename(columns={"from_acct": "acct"})

    to_features = txn.groupby("to_acct").agg(
        to_txn_count=("txn_amt", "count"),
        to_txn_sum=("txn_amt", "sum"),
        to_txn_mean=("txn_amt", "mean"),
        to_unique_from=("from_acct", "nunique"),
    ).reset_index().rename(columns={"to_acct": "acct"})

    features = pd.merge(from_features, to_features, on="acct", how="outer").fillna(0)
    print("ready to merge")
    alert_file = fl.FlyteFile.from_source(alert_path)
    with open(alert_file, "r") as f:
        alert = pd.read_csv(f)
    features = features.merge(alert[["acct"]].assign(label=1), on="acct", how="left")
    features["label"] = features["label"].fillna(0).astype(int)

    features.to_csv("acct_features.csv", index=False)
    return fl.FlyteFile(path="acct_features.csv")