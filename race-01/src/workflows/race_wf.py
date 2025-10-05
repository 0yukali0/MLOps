import flytekit as fl
from src.tasks.process import eda
from src.tasks.train import train_model

@fl.workflow
def race_wf() -> fl.FlyteFile:
    features = eda()
    result = train_model(features)
    return  result