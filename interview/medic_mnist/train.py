
import torch
import torch.nn as nn
import torch.optim as optim

from data import get_loaders
from model import Net


def train(
    dataset: str,
    batch_size: int,
    epochs: int,
    lr: float,
    save_path: str,
    **kwargs
) -> str:
    info, train_loader, _, _ = get_loaders(
        data_flag=dataset, batch_size=batch_size, download=True
    )
    model = Net(info["n_channels"], len(info["label"]))
    task = info["task"]

    criterion = (
        nn.BCEWithLogitsLoss()
        if task == "multi-label, binary-class"
        else nn.CrossEntropyLoss()
    )
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9)

    for epoch in range(epochs):
        print(f"[Train] {epoch}")
        model.train()
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            if task == "multi-label, binary-class":
                targets = targets.float()
            else:
                targets = targets.squeeze().long()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
    torch.save(model.state_dict(), save_path)
    return save_path
