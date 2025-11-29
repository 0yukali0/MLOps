# How to reproduce?
[Ref](https://github.com/ray-project/ray/blob/master/doc/source/ray-overview/examples/e2e-multimodal-ai-workloads/notebooks/01-Batch-Inference.ipynb) provides the dataset. Download the dataset and put it to `s3://data/dog`

```python
from huggingface_hub import snapshot_download
local_path = snapshot_download("openai/clip-vit-base-patch32")
# move the local_path snapshots and bolb to s3://model/patch32
```
