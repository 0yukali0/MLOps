import flytekit as fl

from src.tasks.preprocess import embedding_dog


@fl.workflow
def wf(path: str = "s3://data/dogs") -> fl.FlyteDirectory:
    o1 = embedding_dog(path=path)
    return o1
