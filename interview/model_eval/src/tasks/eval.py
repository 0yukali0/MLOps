import typing
from pathlib import Path

import flytekit as fl
import pandas as pd
from flytekitplugins.deck.renderer import FrameProfilingRenderer, TableRenderer

from src.core.core import compute_model_metric

image_spec = fl.ImageSpec(
    name="general-image", requirements="uv.lock", registry="localhost:30000"
)

frame_image_spec = fl.ImageSpec(
    name="frame-image",
    python_version="3.8",
    packages=["ydata_profiling", "flytekit", "pandas", "flytekitplugins-deck-standard", "scikit-learn"],
    registry="localhost:30000"
)


@fl.task(container_image=image_spec)
def filter(path: str, columns: typing.List[str] = []) -> fl.FlyteFile:
    file = fl.FlyteFile.from_source(path)
    if len(columns) == 0:
        return file
    with open(file) as f:
        df = pd.read_csv(f)
    out_path = str(Path(fl.current_context().working_directory) / "filterd_predict.csv")
    df = df.drop(columns, axis=1)
    df.to_csv(out_path)
    return fl.FlyteFile(path=str(out_path))


@fl.task(container_image=image_spec)
def compute_perf(
    path: typing.Union[str, fl.FlyteFile],
) -> typing.Tuple[float, float, float, float]:
    if isinstance(path, str):
        file = fl.FlyteFile.from_source(path)
    elif isinstance(path, fl.FlyteFile):
        file = path
    with open(file) as f:
        df = pd.read_csv(f)
    return compute_model_metric(df)


@fl.task(enable_deck=True, container_image=frame_image_spec)
def frame_renderer(path: typing.Union[str, fl.FlyteFile]) -> None:
    if isinstance(path, str):
        file = fl.FlyteFile.from_source(path)
    elif isinstance(path, fl.FlyteFile):
        file = path
    with open(file) as f:
        df = pd.read_csv(f)
    fl.Deck("Frame Renderer", FrameProfilingRenderer().to_html(df=df))


@fl.task(enable_deck=True, container_image=image_spec)
def top_frame_renderer(accuracy: float, precision: float, recall: float, auc: float):
    metric = pd.DataFrame(
        data={
            "Accuracy": [accuracy],
            "Precision": [precision],
            "Recall": [recall],
            "AUC": [auc],
        }
    )
    fl.Deck(
        "Model Eval Metric",
        TableRenderer().to_html(df=metric),
    )
