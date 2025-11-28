# Hello World

import flytekit as fl
from src.tasks.preprocess import get_data


@fl.workflow
def wf():
    get_data()
