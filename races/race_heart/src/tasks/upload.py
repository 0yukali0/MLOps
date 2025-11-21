import os
from pathlib import Path

import flytekit as fl

from src.orchestration.constants import load_data_image


@fl.task(
    container_image=load_data_image,
    cache=fl.Cache(version="1.0", serialize=True),
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="20Gi"),
)
def image_2_object() -> fl.FlyteDirectory:
    local_dir = Path(os.getcwd()) / "data"
    return fl.FlyteDirectory(path=str(local_dir))

# yolo11