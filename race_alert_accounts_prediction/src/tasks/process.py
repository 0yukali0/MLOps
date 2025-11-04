import flytekit as fl
import pandas as pd

from src.orchestration.constants import eda_image


@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def download(path: str) -> fl.FlyteFile:
    data = fl.FlyteFile.from_source(path)
    with open(data, "r") as f:
        df = pd.read_csv(f)
    print(df.columns)
    df.to_csv("data.csv")
    return fl.FlyteFile(path="data.csv")


def is_alert_account(
    acct: str,
    alert_df: pd.DataFrame,
) -> bool:
    if acct in alert_df["acct"].values:
        return True
    return False


@fl.task(
    container_image=eda_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="20Gi", cpu="8", ephemeral_storage="20Gi"),
)
def initialize(
    transaction_path: fl.FlyteFile,
    alert_path: fl.FlyteFile,
) -> fl.FlyteFile:
    with open(transaction_path, "r") as f:
        df = pd.read_csv(f)
    print(df.columns)
    with open(alert_path, "r") as f:
        alert_df = pd.read_csv(f)
    print(alert_df.columns)

    # 合併所有帳號（from + to），去重
    from_df = df[["from_acct", "from_acct_type"]].rename(
        columns={"from_acct": "acct", "from_acct_type": "acct_type"}
    )
    to_df = df[["to_acct", "to_acct_type"]].rename(
        columns={"to_acct": "acct", "to_acct_type": "acct_type"}
    )
    all_accts = pd.concat([from_df, to_df], ignore_index=True).drop_duplicates(
        subset=["acct"]
    )

    # 建立 accounts DataFrame
    accounts = pd.DataFrame()
    accounts["acct"] = all_accts["acct"]
    accounts["account_type"] = accounts["acct"].isin(alert_df["acct"]).astype(int)
    accounts["owner_type"] = (all_accts["acct_type"] == "01").astype(int)
    accounts["acct_alert_recv"] = 0
    accounts["acct_alert_send"] = 0

    # 輸出
    accounts.to_csv("result.csv", index=False)
    return fl.FlyteFile(path="result.csv")


@fl.task(
    container_image=eda_image,
    #cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def attach_account_type(
    transaction_path: fl.FlyteFile,
    alert_path: fl.FlyteFile,
    result_path: fl.FlyteFile,
) -> fl.FlyteFile:
    with open(transaction_path, "r") as f:
        transaction_df = pd.read_csv(f)

    with open(alert_path, "r") as f:
        alert_df = pd.read_csv(f)

    with open(result_path, "r") as f:
        result = pd.read_csv(f)

    alert_set = set(alert_df["acct"])
    # 只考慮 from_acct_type 和 to_acct_type == "01"
    from_alert_mask = transaction_df["from_acct"].isin(alert_set)
    to_alert_mask = transaction_df["to_acct"].isin(alert_set)

    # 計算 acct_alert_recv
    recv_counts = (
        transaction_df.loc[to_alert_mask, ["from_acct"]]
        .groupby("from_acct")
        .size()
        .rename("acct_alert_recv")
    )
    result = result.merge(recv_counts, how="left", left_on="acct", right_on="from_acct")
    result["acct_alert_recv"] = result["acct_alert_recv_y"].fillna(0).astype(int)
    result.drop(
        columns=["from_acct", "acct_alert_recv_y"], inplace=True, errors="ignore"
    )

    # 計算 acct_alert_send
    send_counts = (
        transaction_df.loc[from_alert_mask, ["to_acct"]]
        .groupby("to_acct")
        .size()
        .rename("acct_alert_send")
    )
    result = result.merge(send_counts, how="left", left_on="acct", right_on="to_acct")
    result["acct_alert_send"] = result["acct_alert_send_y"].fillna(0).astype(int)
    result.drop(columns=["to_acct", "acct_alert_send_y"], inplace=True, errors="ignore")

    result.to_csv("result.csv")
    return fl.FlyteFile(path="result.csv")
