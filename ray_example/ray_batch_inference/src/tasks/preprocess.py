from pathlib import Path

import flytekit as fl
import ray
from flytekitplugins.ray import HeadNodeConfig, RayJobConfig, WorkerNodeConfig

from src.core.core import EmbedImages, add_class

image_spec = fl.ImageSpec(
    name="ray",
    requirements="uv.lock",
    apt_packages=["wget"],
    registry="localhost:30000",
)

ray_config = RayJobConfig(
    head_node_config=HeadNodeConfig(limits=fl.Resources(mem="10Gi", cpu="3", gpu=1)),
    worker_node_config=[
        WorkerNodeConfig(
            group_name="ray-group",
            replicas=0,
            limits=fl.Resources(mem="10Gi", cpu="3", gpu=1),
        )
    ],
    runtime_env={},
    enable_autoscaling=False,
    shutdown_after_job_finishes=True,
    ttl_seconds_after_finished=30,
)


@fl.task(
    task_config=ray_config,
    requests=fl.Resources(mem="2Gi", cpu="1"),
    container_image=image_spec,
)
def embedding_dog(path: str) -> fl.FlyteDirectory:
    d = fl.FlyteDirectory.from_source(source=path)
    local_path = d.download()
    """
    s3_fs = pafs.S3FileSystem(
        access_key=os.getenv("FLYTE_AWS_ACCESS_KEY_ID", default="minio"),
        secret_key=os.getenv("FLYTE_AWS_SECRET_ACCESS_KEY", default="miniostorage"),
        endpoint_override=os.getenv("FLYTE_AWS_ENDPOINT", default="http://minio.default.svc.cluster.local:9000"),
        scheme="http"
    )
    """
    ray_local_path = "local://" + f"{local_path}"
    embeddings_path = str(Path(fl.current_context().working_directory) / "result")
    ds = ray.data.read_parquet(
        ray_local_path,
        # filesystem=s3_fs,
        include_paths=True,
        shuffle="files",
    )
    ds = ds.map(add_class)
    embeddings_ds = ds.map(
        EmbedImages(
            model_id="s3://model/patch32",
        ),
        concurrency=4,
        num_gpus=1,
    )
    embeddings_ds = embeddings_ds.drop_columns(["image"])
    embeddings_ds.write_parquet(embeddings_path)
    return fl.FlyteDirectory(path=embeddings_path)
