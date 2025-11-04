import flytekit as fl

from src.tasks.process import attach_account_type, download, initialize
from src.tasks.train import train_model


@fl.workflow
def race_wf(
    transaction_path: str = "s3://data/acct_transaction.csv",
    acct_alert_path: str = "s3://data/acct_alert.csv",
) -> fl.FlyteFile:
    transaction_df_path = download(path=transaction_path)
    acct_alert_df_path = download(path=acct_alert_path)
    acct_path = initialize(
        transaction_path=transaction_df_path, alert_path=acct_alert_df_path
    )
    # frame_renderer(data=acct_path)
    feature_path = attach_account_type(
        transaction_path=transaction_df_path,
        alert_path=acct_alert_df_path,
        result_path=acct_path,
    )
    # frame_renderer(data=acct_path)
    result = train_model(feature_path=feature_path)
    return result
