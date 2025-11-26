import flytekit as fl
from dask import array as da
from flytekitplugins.dask import Dask, WorkerGroup
import os
import typing
import ray
from flytekitplugins.ray import HeadNodeConfig, RayJobConfig, WorkerNodeConfig


image_spec = fl.ImageSpec(
    name="dask-dataframe",
    requirements="uv.lock",
    registry="localhost:30000"
)

ray_image = fl.ImageSpec(
    name="ray-dataframe",
    requirements="uv.lock",
    registry="localhost:30000",
    apt_packages=["wget"],
)

@ray.remote
def f(x: int) -> int:
    return x * x

ray_config = RayJobConfig(
    head_node_config=HeadNodeConfig(ray_start_params={"log-color": "True"}),
    worker_node_config=[WorkerNodeConfig(group_name="ray-group", replicas=1)],
    runtime_env={"pip": ["numpy", "pandas"]},  # or runtime_env="./requirements.txt"
    enable_autoscaling=False,
    shutdown_after_job_finishes=True,
    ttl_seconds_after_finished=3600,
)

@fl.task(
    task_config=ray_config,
    requests=fl.Resources(mem="4Gi", cpu="2"),
    container_image=ray_image,
)
def ray_task(n: int) -> typing.List[int]:
    futures = [f.remote(i) for i in range(n)]
    return ray.get(futures)

@fl.task(
    task_config=Dask(
        workers=WorkerGroup(
            number_of_workers=2,
            requests=fl.Resources(cpu="4", mem="10Gi"),
            limits=fl.Resources(cpu="4", mem="10Gi"),
        ),
    ),
    container_image=image_spec,
)
def hello_dask(size: int) -> float:
    array = da.random.random(size)
    return float(array.mean().compute())
