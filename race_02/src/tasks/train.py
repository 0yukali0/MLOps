import flytekit as fl
from ultralytics import YOLO

from src.orchestration.constants import yolo_image


@fl.task(
    container_image=yolo_image,
    limits=fl.Resources(mem="10Gi", cpu="2", ephemeral_storage="10Gi"),
)
def train_yolov8() -> fl.FlyteFile:
    model = YOLO("yolov8n.pt")
    results = model.train(data="coco8.yaml", epochs=10, imgsz=640)
    best_weight_path = f"{results.save_dir}/weights/best.pt"
    return fl.FlyteFile(path=best_weight_path)
