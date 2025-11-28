import flytekit as fl
import ray
import os
import pyarrow.fs as pafs
from flytekitplugins.ray import HeadNodeConfig, RayJobConfig, WorkerNodeConfig

image_spec = fl.ImageSpec(
    name="say-hello-image",
    requirements="uv.lock",
    apt_packages=["wget"],
    registry="localhost:30000"
)

ray_config = RayJobConfig(
    head_node_config=HeadNodeConfig(limits=fl.Resources(mem="7Gi", cpu="4")),
    worker_node_config=[WorkerNodeConfig(group_name="ray-group", replicas=0, limits=fl.Resources(mem="4Gi", cpu="2"))],
    runtime_env={},
    enable_autoscaling=False,
    shutdown_after_job_finishes=True,
    ttl_seconds_after_finished=20,
)


@fl.task(
    task_config=ray_config,
    requests=fl.Resources(mem="2Gi", cpu="1"),
    container_image=image_spec,
)
def get_data():
    s3_fs = pafs.S3FileSystem(
        access_key=os.getenv("BOLB_KEY", default="minio"),
        secret_key=os.getenv("BOLB_PW", default="miniostorage"),
        endpoint_override=os.getenv("BOLB_ENDPOINT", default="http://minio.svc.default.cluster.local:9000"),
        scheme="http"
    )

    ds = ray.data.read_parquet(
        "data/tmp/",
        filesystem=s3_fs,
        include_paths=True, 
        shuffle="files",
    )