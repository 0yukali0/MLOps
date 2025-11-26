import torch
from medmnist import Evaluator

from data import get_loaders
from model import Net


def test(model_path: str, dataset: str, batch_size: int, split: str, **kwargs):
    info, _, train_loader_at_eval, test_loader = get_loaders(
        data_flag=dataset, batch_size=batch_size, download=True
    )
    model = Net(info["n_channels"], len(info["label"]))
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    y_true = torch.tensor([])
    y_score = torch.tensor([])
    data_loader = train_loader_at_eval if split == "train" else test_loader

    with torch.no_grad():
        for inputs, targets in data_loader:
            outputs = model(inputs)

            if info.get("task", "") == "multi-label, binary-class":
                targets = targets.to(torch.float32)
                outputs = outputs.softmax(dim=-1)
            else:
                targets = targets.squeeze().long()
                outputs = outputs.softmax(dim=-1)
                targets = targets.float().resize_(len(targets), 1)

            y_true = torch.cat((y_true, targets), 0)
            y_score = torch.cat((y_score, outputs), 0)

        y_true = y_true.numpy()
        y_score = y_score.detach().numpy()

        evaluator = Evaluator(dataset, split)
        metrics = evaluator.evaluate(y_score)

        print("%s  auc: %.3f  acc:%.3f" % (split, *metrics))
