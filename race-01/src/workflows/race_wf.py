import flytekit as fl
from src.tasks.process import fetch, normalize
from src.tasks.visual import frame_renderer

@fl.workflow
def race_wf(transaction_path: str ="s3://data/accounts/acct_transaction.csv") -> fl.FlyteFile:
    transaction_data = fetch(path=transaction_path)
    frame_renderer(transaction_data)
    normal_transaction_data = normalize(transaction_data)
    frame_renderer(normal_transaction_data)
    return normal_transaction_data