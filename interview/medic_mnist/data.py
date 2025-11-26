import medmnist
import torch.utils.data as data
import torchvision.transforms as transforms
from medmnist import INFO


def get_loaders(
    data_flag: str = "pathmnist", batch_size: int = 128, download: bool = True
):
    info = INFO[data_flag]
    DataClass = getattr(medmnist, info["python_class"])

    data_transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize(mean=[0.5], std=[0.5])]
    )

    train_dataset = DataClass(
        split="train", transform=data_transform, download=download
    )
    test_dataset = DataClass(split="test", transform=data_transform, download=download)

    train_loader_eval = data.DataLoader(
        dataset=train_dataset, batch_size=2 * batch_size, shuffle=False
    )

    train_loader = data.DataLoader(
        dataset=train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = data.DataLoader(
        dataset=test_dataset, batch_size=2 * batch_size, shuffle=False
    )

    return info, train_loader, train_loader_eval, test_loader
