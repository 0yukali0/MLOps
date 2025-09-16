import flytekit as fl

import torch
from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision.models import resnet18
from torchvision.datasets import FashionMNIST
from torchvision.transforms import ToTensor, Normalize, Compose

image_spec = fl.ImageSpec(
    name="pytorch-resnet", requirements="uv.lock", registry="localhost:30000"
)


@fl.task(container_image=image_spec)
def download_data(data_path: str) -> fl.FlyteDirectory:
    FashionMNIST(root=data_path, train=True, download=True, transform=None)
    return fl.FlyteDirectory(path=data_path)

@fl.task(container_image=image_spec)
def train(epoch: int, lr: float, fd: fl.FlyteDirectory) -> fl.FlyteFile:
    """
    1. Data to dataloader
    2. train model and save the weight
    """
    fd.download()
    transform = Compose([ToTensor(), Normalize((0.28604,), (0.32025,))])
    train_data = FashionMNIST(
        root=fd.path, train=True, download=False, transform=transform
    )
    train_loader = DataLoader(train_data, batch_size=128, shuffle=True)

    model = resnet18(num_classes=10)
    model.conv1 = torch.nn.Conv2d(
        1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False
    )
    model.to("cpu")
    criterion = CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=lr)
    wieght_path = str(fl.current_context().working_directory) + "/model.pt"
    for current_epoch in range(epoch):
        for images, labels in train_loader:
            images, labels = images.to("cpu"), labels.to("cpu")
            outputs = model(images)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        metrics = {"loss": loss.item(), "epoch": current_epoch}
        print(metrics)
    torch.save(model.state_dict(), checkpoint_path)
    return fl.FlyteFile(path=wieght_path)


@fl.workflow
def train_resnet_wf(epoch: int = 5, lr: float = 0.001, data_path: str = "/tmp/data") -> fl.FlyteFile:
    data = download_data(data_path)
    weight_file = train(epoch, lr, data)
    return weight_file
