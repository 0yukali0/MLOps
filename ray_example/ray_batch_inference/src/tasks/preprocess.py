import flytekit as fl
import ray
import os
import pyarrow.fs as pafs
from flytekitplugins.ray import HeadNodeConfig, RayJobConfig, WorkerNodeConfig

image_spec = fl.ImageSpec(
    name="ray",
    requirements="uv.lock",
    apt_packages=["wget"],
    registry="localhost:30000"
)

ray_config = RayJobConfig(
    head_node_config=HeadNodeConfig(limits=fl.Resources(mem="2Gi", cpu="1")),
    worker_node_config=[WorkerNodeConfig(group_name="ray-group", replicas=1, limits=fl.Resources(mem="2Gi", cpu="1"))],
    runtime_env={},
    enable_autoscaling=False,
    shutdown_after_job_finishes=True,
    ttl_seconds_after_finished=20,
)


@fl.task(
    task_config=ray_config,
    requests=fl.Resources(mem="6Gi", cpu="3"),
    container_image=image_spec,
)
def get_data():
    s3_fs = pafs.S3FileSystem(
        access_key=os.getenv("FLYTE_AWS_ACCESS_KEY_ID", default="minio"),
        secret_key=os.getenv("FLYTE_AWS_SECRET_ACCESS_KEY", default="miniostorage"),
        endpoint_override=os.getenv("FLYTE_AWS_ENDPOINT", default="http://minio.default.svc.cluster.local:9000"),
        scheme="http"
    )

    ds = ray.data.read_parquet(
        "data/tmp/",
        filesystem=s3_fs,
        include_paths=True, 
        shuffle="files",
    )