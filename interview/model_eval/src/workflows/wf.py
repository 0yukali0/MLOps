import flytekit as fl

from src.tasks.eval import filter, compute_perf, top_frame_renderer, frame_renderer


@fl.workflow
def eval_wf(path: str = "s3://data/psudo_result.csv") -> None:
    data = filter(path=path, columns=["Sample ID", "AI pred"])
    frame_renderer(path=data)

    accuracy, precision, recall, auc = compute_perf(path=path)
    top_frame_renderer(accuracy=accuracy, precision=precision, recall=recall, auc=auc)
