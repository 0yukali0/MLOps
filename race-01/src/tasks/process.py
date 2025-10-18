import flytekit as fl
import pandas as pd
from src.orchestration.constants import (
    eda_image,
    acct_transaction_cols,
    acct_alert_cols,
)
from flytekit.types.structured.structured_dataset import StructuredDataset
from typing_extensions import Annotated


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
