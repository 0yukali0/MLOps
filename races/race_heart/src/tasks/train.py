import flytekit as fl
from ultralytics import YOLO

from src.orchestration.constants import yolo_image


@fl.task(
    container_image=yolo_image,
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="10Gi"),
)
def train_yolov8(
    data: fl.FlyteDirectory,
    yolo_version: str = "yolov8n.pt",
    epochs: int = 10,
    iamge_size: int = 512,
) -> fl.FlyteFile:
    model = YOLO(yolo_version)
    results = model.train(data="coco8.yaml", epochs=epochs, imgsz=iamge_size)
    best_weight_path = f"{results.save_dir}/weights/best.pt"
    return fl.FlyteFile(path=best_weight_path)

@fl.task(
    container_image=yolo_image,
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="10Gi"),
)
def train_nas(
    data: fl.FlyteDirectory,
    yolo_version: str = "yolo_nas_s.pt",
    epochs: int = 10,
    iamge_size: int = 512,
) -> fl.FlyteFile:
    model = YOLO(yolo_version)
    results = model.train(data="coco8.yaml", epochs=epochs, imgsz=iamge_size)
    best_weight_path = f"{results.save_dir}/weights/best.pt"
    return fl.FlyteFile(path=best_weight_path)
