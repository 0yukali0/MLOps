from pathlib import Path

import flytekit as fl
import pydicom

from src.core.core import align_hand_xray, save_processed_dicom, remove_black_background
from src.core.utils import unzip, zip_dir

image_spec = fl.ImageSpec(
    name="say-hello-image", requirements="uv.lock", registry="localhost:30000"
)


@fl.task(container_image=image_spec)
def process_dcm(source: str) -> fl.FlyteFile:
    data_dir = Path(fl.current_context().working_directory) / "dcm_files"
    data_dir.mkdir(exist_ok=True)
    local_dir = Path(fl.current_context().working_directory) / "handled_dcm_files"
    local_dir.mkdir(exist_ok=True)

    data = fl.FlyteFile(path=source)
    data_path = data.download()
    unzip(data_path, data_dir)
    files = fl.FlyteDirectory.listdir(fl.FlyteDirectory(path=str(data_dir)))
    print(len(files))
    for file in files:
        ds = pydicom.dcmread(file)
        img = ds.pixel_array
        cropped_img = remove_black_background(img)
        aligned_img = align_hand_xray(cropped_img)
        #final_img = remove_black_background(aligned_img)
        old_id, new_id = save_processed_dicom(ds, aligned_img, local_dir)
        print(f"{old_id} -> {new_id}")
    ouput_path = str(Path(fl.current_context().working_directory) / "handled_dcm.zip")
    zip_dir(local_dir, ouput_path)
    return fl.FlyteFile(path=ouput_path)
