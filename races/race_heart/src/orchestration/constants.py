from flytekit import ImageSpec

PYTHON_VERSION = "3.12"
REGISTRY_URI = "localhost:30000"

load_data_image = ImageSpec(
    name="image_with_copy",
    copy=["data"],
    python_version=PYTHON_VERSION,
    registry=REGISTRY_URI,
)

yolo_image = ImageSpec(
    name="yolo_v8",
    packages=["ultralytics==8.3.217"],
    apt_packages=["libgl1", "libglib2.0-0"],
    python_version=PYTHON_VERSION,
    registry=REGISTRY_URI,
)
