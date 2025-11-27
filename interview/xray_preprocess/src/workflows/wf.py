import flytekit as fl
import typing

from src.tasks.preprocess import process_dcm


@fl.workflow
def wf(path: str = "s3://data/HandBoneXRay.zip") -> typing.Tuple[fl.FlyteFile, fl.FlyteFile]:
    img, map_id = process_dcm(source=path)
    return img, map_id
