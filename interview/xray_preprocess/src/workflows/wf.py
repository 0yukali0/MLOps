import flytekit as fl

from src.tasks.preprocess import process_dcm


@fl.workflow
def wf(path: str = "s3://data/HandBoneXRay.zip") -> fl.FlyteFile:
    f = process_dcm(source=path)
    return f
