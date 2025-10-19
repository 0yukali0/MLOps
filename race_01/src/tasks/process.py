import flytekit as fl
import pandas as pd
from flytekit.types.structured.structured_dataset import StructuredDataset
from typing_extensions import Annotated

from src.orchestration.constants import (
    acct_alert_cols,
    acct_cols,
    acct_transaction_cols,
    eda_image,
)


@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def load_acct_transaction(
    path: str,
) -> Annotated[StructuredDataset, acct_transaction_cols]:
    data = fl.FlyteFile.from_source(path)
    with open(data, "r") as f:
        df = pd.read_csv(f)
    return StructuredDataset(dataframe=df)

@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def load_acct_alert(path: str) -> Annotated[StructuredDataset, acct_alert_cols]:
    data = fl.FlyteFile.from_source(path)
    with open(data, "r") as f:
        df = pd.read_csv(f)
    return StructuredDataset(dataframe=df)

@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def initialize(
    df: Annotated[StructuredDataset, acct_transaction_cols],
) -> Annotated[StructuredDataset, acct_cols]:
    df = df.open(pd.DataFrame).all()
    acct_cols = [
        "acct",
        "account_type",
        "owner_type",
        "acct_alert_recv",
        "acct_alert_send",
    ]
    accounts = pd.DataFrame(columns=acct_cols)
    for row in df.itertuples(index=False):
        if row.from_acct_type == "01":
            acct: str = row.from_acct
            if acct not in accounts["acct"].values:
                accounts.loc[len(accounts)] = {
                    "acct": acct,
                    "account_type": 0,
                    "owner_type": 0,
                    "acct_alert_recv": 0,
                    "acct_alert_send": 0,
                }
        if row.to_acct_type == "01":
            acct: str = row.to_acct
            if acct not in accounts["acct"].values:
                accounts.loc[len(accounts)] = {
                    "acct": acct,
                    "account_type": 0,
                    "owner_type": 0,
                    "acct_alert_recv": 0,
                    "acct_alert_send": 0,
                }
    return StructuredDataset(dataframe=accounts)

@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def attach_account_type(df: Annotated[StructuredDataset, acct_cols], alert_df: Annotated[StructuredDataset, acct_alert_cols]) -> Annotated[StructuredDataset, acct_cols]:
    df = df.open(pd.DataFrame).all()
    for row in df.itertuples(index=False):
        from_acct_is_alert = False
        to_acct_is_alert = False
        if row.from_acct_type == "01":
            acct = row.from_acct
            from_acct_is_alert = is_alert_account(acct=acct, alert_df=alert_df)

        if row.to_acct_type == "01":
            acct = row.to_acct
            to_acct_is_alert = is_alert_account(acct=acct, alert_df=alert_df)

        if row.from_acct_type == "01" and to_acct_is_alert:
            df.loc[df["acct"] == row.from_acct, "acct_alert_recv"] += 1
            
        if row.to_acct_type == "01" and from_acct_is_alert:
            df.loc[df["acct"] == row.to_acct, "acct_alert_send"] += 1

    return StructuredDataset(dataframe=df)

@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="5Gi", cpu="1", ephemeral_storage="10Gi"),
)
def is_alert_account(acct: str, alert_df: Annotated[StructuredDataset, acct_alert_cols]) -> bool:
    alert_df = alert_df.open(pd.DataFrame).all()
    if acct in accounts["acct"].values:
        return True
    return False