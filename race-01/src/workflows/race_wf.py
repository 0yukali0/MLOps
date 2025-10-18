import flytekit as fl
from src.tasks.process import load_acct_transaction, load_acct_alert


@fl.workflow
def race_wf(
    transaction_path: str = "s3://data/acct_transaction.csv",
    acct_alert_path: str = "s3://data/acct_alert.csv",
):
    acct_transaction_data = load_acct_transaction(path=transaction_path)
    acct_alert_data = load_acct_alert(path=acct_alert_path)
