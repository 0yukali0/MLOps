from flytekit import ImageSpec, kwtypes

REGISTRY_URI = "localhost:30000"
PYTHON_VERSION = "3.12"

# original csv format
acct_transaction_cols = kwtypes(
    from_acct=str,
    from_acct_type=str,
    to_acct=str,
    to_acct_type=str,
    is_self_txn=str,
    txn_amt=int,
    txn_date=str,
    txn_time=str,
    currency_type=str,
    channel_type=str,
)

acct_alert_cols = kwtypes(acct=str, event_date=str)

# result cols
acct_cols = kwtypes(
    acct=str, account_type=int, owner_type=int, acct_alert_recv=int, acct_alert_send=int
)

local_data_image = ImageSpec(name="local_csv", copy=["data"], registry=REGISTRY_URI)

eda_image = ImageSpec(
    name="k9s",
    packages=["pandas==2.3.3", "pyarrow", "fastparquet"],
    python_version=PYTHON_VERSION,
    registry=REGISTRY_URI,
)

xgb_train_image = ImageSpec(
    name="xgb_model",
    packages=[
        "xgboost==3.0.5",
        "pandas==2.3.3",
        "scikit-learn==1.7.2",
        "pyarrow",
        "fastparquet",
    ],
    python_version=PYTHON_VERSION,
    registry=REGISTRY_URI,
)

visual_image = ImageSpec(
    name="visual_tools",
    packages=[
        "pandas==2.3.3",
        "flytekitplugins-deck-standard",
        "ydata-profiling",
        "pyarrow",
        "fastparquet",
    ],
    python_version=PYTHON_VERSION,
    registry=REGISTRY_URI,
)
