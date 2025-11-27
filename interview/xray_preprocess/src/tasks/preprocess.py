import typing
from pathlib import Path

import flytekit as fl
import pandas as pd
import pydicom

from src.core.core import align_hand_xray, remove_black_background, save_processed_dicom
from src.core.utils import unzip, zip_dir

image_spec = fl.ImageSpec(
    name="general",
    requirements="uv.lock",
    apt_packages=["libgl1", "libglib2.0-0", "libsm6", "libxrender1", "libxext6"],
    registry="localhost:30000",
)


@fl.task(container_image=image_spec)
def process_dcm(source: str) -> typing.Tuple[fl.FlyteFile, fl.FlyteFile]:
    data_dir = Path(fl.current_context().working_directory) / "dcm_files"
    data_dir.mkdir(exist_ok=True)
    local_dir = Path(fl.current_context().working_directory) / "handled_dcm_files"
    local_dir.mkdir(exist_ok=True)
    data = fl.FlyteFile(path=source)
    data_path = data.download()
    unzip(data_path, data_dir)
    files = fl.FlyteDirectory.listdir(fl.FlyteDirectory(path=str(data_dir)))
    map_df = pd.DataFrame(columns=["origin_uuid", "new_uuid"])
    for file in files:
        ds = pydicom.dcmread(file)
        img = ds.pixel_array
        cropped_img = remove_black_background(img)
        aligned_img = align_hand_xray(cropped_img)
        old_id, new_id = save_processed_dicom(ds, aligned_img, local_dir)
        map_df.loc[len(map_df)] = {"origin_uuid": old_id, "new_uuid": new_id}
    ouput_path = str(Path(fl.current_context().working_directory) / "handled_dcm.zip")
    map_path = str(Path(fl.current_context().working_directory) / "uuid_map.csv")
    map_df.to_csv(map_path)
    zip_dir(local_dir, ouput_path)
    return fl.FlyteFile(path=ouput_path), fl.FlyteFile(path=map_path)
