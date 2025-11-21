import flytekit as fl

from src.tasks.train import train_yolov8
from src.tasks.upload import image_2_object


@fl.workflow()
def main_wf() -> fl.FlyteFile:
    data_dir = image_2_object()
    model_pt = train_yolov8()
    return model_pt
