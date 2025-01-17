# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_functional.ipynb.

# %% auto 0
__all__ = ['sigmoid', 'softmax', 'relu', 'BCE_loss', 'CrossEntropy_loss', 'dropout']

# %% ../nbs/02_functional.ipynb 2
import numpy as np
from tidygrad.tensor import Tensor, UnaryElementwiseOp, BinaryElementwiseOp, ExpLog

# %% ../nbs/02_functional.ipynb 3
class Sigmoid(UnaryElementwiseOp):
    """Take the sigmoid of a tensor"""

    name_template = "sigmoid({})"

    def __init__(self, a, name=None):
        super().__init__(a, name=name)
        self.out = Tensor(1 / (1 + np.exp(-self.args[0].data)), name=self.name, op=self)

    def backward(self):
        with np.errstate(under="ignore"):  # Triggered by infinitesimally small 1-data
            self.parents[0].grad += self.out.grad * self.out.data * (1 - self.out.data)

# %% ../nbs/02_functional.ipynb 4
def sigmoid(input, name=None):
    return Sigmoid(input, name=name).out

# %% ../nbs/02_functional.ipynb 5
def softmax(input, name=None):
    exp = input.exp()
    return exp.div(exp.sum(axis=-1, keepdims=True), name=name)

# %% ../nbs/02_functional.ipynb 6
class Relu(UnaryElementwiseOp):
    """Take the sigmoid of a tensor"""

    name_template = "relu({})"

    def __init__(self, a, name=None):
        super().__init__(a, name=name)
        self.out = Tensor(np.maximum(0, self.args[0].data), name=self.name, op=self)

    def backward(self):
        self.parents[0].grad += self.out.grad * (self.out.data > 0)

# %% ../nbs/02_functional.ipynb 7
def relu(input, name=None):
    return Relu(input, name=name).out

# %% ../nbs/02_functional.ipynb 8
def BCE_loss(logits: Tensor, target: Tensor, reduction="mean"):
    loss = logits - logits * target + ExpLog(-logits).out
    if reduction == "mean":
        return loss.mean()
    if reduction == "sum":
        return loss.sum()
    assert 0, "Invalid reduction"

# %% ../nbs/02_functional.ipynb 9
def CrossEntropy_loss(logits: Tensor, target: Tensor, reduction="mean"):
    if not isinstance(target, Tensor):
        target = Tensor(target)
    sm = softmax(logits)
    loss = -target * sm.log()
    if reduction == "mean":
        return loss.mean()
    if reduction == "sum":
        return loss.sum()
    assert 0, "Invalid reduction"

# %% ../nbs/02_functional.ipynb 11
class Dropout(UnaryElementwiseOp):
    """Apply Dropout to a tensor"""

    name_template = "dropout({})"

    def __init__(self, a, p_drop=0.1, training=True, name=None):
        super().__init__(a, name=name)
        assert 0 < p_drop < 1, f"p_drop must in (0, 1), got {p_drop}"
        self.p_drop = p_drop
        self.training = training
        if training:
            # Note: We scale up the outputs during training rather than scaling down during inference.
            scale_factor = 1 / (1 - p_drop)
            self.mask = np.random.binomial(
                scale_factor, 1 - p_drop, size=self.args[0].data.shape
            )
            self.out = Tensor(self.args[0].data * self.mask, name=self.name, op=self)
        else:
            self.out = Tensor(self.args[0].data, name=self.name, op=self)

    def backward(self):
        self.parents[0].grad += self.out.grad * (self.mask if self.training else 1)

# %% ../nbs/02_functional.ipynb 12
def dropout(x, p=0.5, training=True):
    if p == 0:
        return x

    return Dropout(x, p_drop=p, training=training).out
