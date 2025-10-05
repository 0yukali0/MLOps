from flytekit import ImageSpec

registry_path = "localhost:30000"

local_data_image = ImageSpec(
    name="local_csv",
    copy=["data"],
    registry=registry_path
)

eda_image = ImageSpec(
    name="eda",
    packages=["pandas==2.3.3"],
    python_version="3.12",
    registry=registry_path
)

xgb_train_image = ImageSpec(
    name="xgb_model",
    packages=["xgboost==3.0.5", "pandas==2.3.3", "scikit-learn==1.7.2"],
    python_version="3.12",
    registry=registry_path
)