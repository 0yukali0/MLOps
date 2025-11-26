# Hello World

import flytekit as fl
from xray_preprocess.src.tasks.preprocess import say_hello


@fl.workflow
def hello_world_wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
