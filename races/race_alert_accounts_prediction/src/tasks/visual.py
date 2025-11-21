import flytekit as fl
import pandas as pd
from flytekitplugins.deck.renderer import FrameProfilingRenderer

from src.orchestration.constants import visual_image


@fl.task(
    enable_deck=True,
    container_image=visual_image,
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def frame_renderer(data: fl.FlyteFile) -> None:
    with open(data, "r") as f:
        df = pd.read_csv(f)
    fl.Deck("Frame Renderer", FrameProfilingRenderer().to_html(df=df))
