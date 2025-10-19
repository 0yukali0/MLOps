import flytekit as fl
from src.tasks.process import initialize, load_acct_alert, load_acct_transaction, attach_account_type

@fl.workflow
def race_wf(
    transaction_path: str = "s3://data/acct_transaction.csv",
    acct_alert_path: str = "s3://data/acct_alert.csv",
):
    
    acct_transaction_data = load_acct_transaction(path=transaction_path)
    acct_alert_data = load_acct_alert(path=acct_alert_path)
    acct = initialize(df=acct_transaction_data)
    acct = attach_account_type(df=acct, alert_df=acct_alert_data)
