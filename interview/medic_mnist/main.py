import argparse
from test import test
from train import train

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="pathmnist")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--save_path", type=str, default="model.pth")
    args = parser.parse_args()
    model_path = train(**vars(args))
    test(model_path=model_path, split="train", **vars(args))
    test(model_path=model_path, split="test", **vars(args))
