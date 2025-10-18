import flytekit as fl
from src.tasks.visual import frame_renderer


@fl.workflow
def visual_wf():
    frame_renderer(uri="s3://data/accounts/acct_transaction.csv")
    frame_renderer(uri="s3://data/accounts/acct_alert.csv")
