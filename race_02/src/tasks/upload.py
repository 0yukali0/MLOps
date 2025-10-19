import flytekit as fl
from src.orchestration.constants import load_data_image

@fl.task(container_image=load_data_image)
def image_2_object() -> fl.FlyteDirectory:
    working_dir = fl.current_context().working_directory
    local_dir = Path(working_dir) / "data"
    return FlyteDirectory(path=str(local_dir))