import flytekit as fl

image_spec = fl.ImageSpec(
    name="say-hello-image",
    requirements="uv.lock"
    registry="localhost:30000"
)


@fl.task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello register, {name}!"
