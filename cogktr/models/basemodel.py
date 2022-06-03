import torch.nn as nn


class BaseModel(nn.Module):
    def __init__(self):
        super().__init__()

    def loss(self, batch, loss_function):
        pass

    def forward(self, *args):
        pass

    def evaluate(self, batch, metric_function):
        pass

    def predict(self, *args):
        pass

    def get_batch(self, batch):
        pass
