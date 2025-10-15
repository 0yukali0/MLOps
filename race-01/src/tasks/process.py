import flytekit as fl
import pandas as pd
from src.core.encoding import encode
from src.orchestration.constants import eda_image
from typing_extensions import Annotated
from flytekit.types.structured.structured_dataset import StructuredDataset


@fl.task(container_image=eda_image, cache=fl.Cache(version="1.0", serialize=True), limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"))
def fetch(path: str) -> fl.FlyteFile:
    data = fl.FlyteFile.from_source(path)
    with open(data, "r") as f:
        df = pd.read_csv(f)
    return data

@fl.task(container_image=eda_image, limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"))
def normalize(data: fl.FlyteFile) -> fl.FlyteFile:
    '''
    currency_type normalization
    channel_type normalization
    '''
    with open(data, "r") as f:
        df = pd.read_csv(f)
    df['currency_type']= encode(df['currency_type'])
    df['channel_type'] = encode(df['channel_type'])
    df.to_csv("normal_acct_transaction.csv", index=False)
    return fl.FlyteFile(path="normal_acct_transaction.csv")

@fl.task(container_image=eda_image, limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"))
def normalize(data: fl.FlyteFile) -> fl.FlyteFile: