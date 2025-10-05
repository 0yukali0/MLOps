import flytekit as fl
import csv

@fl.task
def load_s3_dir(uri: str = "s3://data/accounts") -> fl.FlyteDirectory:
    return fl.FlyteDirectory(uri)

@fl.task
def load_s3_data(uri: str = "s3://data/accounts/acct_transaction.csv") -> fl.FlyteFile:
    return fl.FlyteFile(path=remote_path)
