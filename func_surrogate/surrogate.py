import os
from typing import Literal
from dataclasses import dataclass

import matplotlib.pyplot as plt
import torch
import torch.nn as nn


torch.manual_seed(42)


@dataclass
class ExperimentConfig:
    name: str
    hidden_dim: int
    epochs: int
    lr: float
    num_points: int
    training_ratio: float = 0.8
    activation: Literal["tanh", "relu", "sigmoid"] = "tanh"


class SurrogateNet(nn.Module):
    """
    1-N-1 neural network:
    1 input neuron, N hidden neurons, 1 output neuron.
    """

    def __init__(self, hidden_dim: int, activation: str = "tanh") -> None:
        super().__init__()
        if activation == "tanh":
            act_layer = nn.Tanh()
        elif activation == "relu":
            act_layer = nn.ReLU()
        elif activation == "sigmoid":
            act_layer = nn.Sigmoid()
        else:
            raise ValueError(f"Unsupported activation: {activation}")
        self.net = nn.Sequential(
            nn.Linear(1, hidden_dim),
            act_layer,
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def target_function(p: torch.Tensor) -> torch.Tensor:
    """
    g(p) = 1 + sin((3*pi/2) * p)
    Period T = 4/3
    """
    return 1 + torch.sin((3 * torch.pi / 2) * p)


def normalize_to_minus1_1(x: torch.Tensor, x_min: float, x_max: float) -> torch.Tensor:
    """
    Normalize x from [x_min, x_max] to [-1, 1].
    """
    return 2.0 * (x - x_min) / (x_max - x_min) - 1.0


def compute_metrics(y_true: torch.Tensor, y_pred: torch.Tensor) -> dict:
    mse = torch.mean((y_pred - y_true) ** 2).item()
    rmse = mse**0.5
    mae = torch.mean(torch.abs(y_pred - y_true)).item()
    return {
        "mse": mse,
        "rmse": rmse,
        "mae": mae,
    }


def make_dataset(
    num_points: int,
    T: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Returns:
        p_raw: raw input in [0, T]
        p_norm: normalized input in [-1, 1]
        y: target values
    """
    p_raw = torch.linspace(0.0, T, num_points).unsqueeze(1)
    y = target_function(p_raw)
    p_norm = normalize_to_minus1_1(p_raw, 0.0, T)
    return p_raw, p_norm, y


def split_dataset(
    x: torch.Tensor,
    y: torch.Tensor,
    train_ratio: float = 0.8,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    split_idx = int(train_ratio * len(x))
    x_train, x_val = x[:split_idx], x[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    return x_train, y_train, x_val, y_val


def train_model(
    model: nn.Module,
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_val: torch.Tensor,
    y_val: torch.Tensor,
    epochs: int,
    lr: float,
) -> tuple[list[float], list[float]]:
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    train_losses: list[float] = []
    val_losses: list[float] = []

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        y_pred_train = model(x_train)
        train_loss = loss_fn(y_pred_train, y_train)
        train_loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            y_pred_val = model(x_val)
            val_loss = loss_fn(y_pred_val, y_val)

        train_losses.append(train_loss.item())
        val_losses.append(val_loss.item())

        if epoch % 200 == 0 or epoch == epochs - 1:
            print(
                f"Epoch {epoch:4d} | "
                f"Train Loss: {train_loss.item():.6f} | "
                f"Val Loss: {val_loss.item():.6f}"
            )

    return train_losses, val_losses


def plot_fit(
    save_dir: str,
    title: str,
    p_data: torch.Tensor,
    y_data: torch.Tensor,
    p_plot: torch.Tensor,
    y_true_plot: torch.Tensor,
    y_pred_plot: torch.Tensor,
) -> None:
    plt.figure(figsize=(8, 5))
    plt.scatter(
        p_data.numpy(),
        y_data.numpy(),
        s=30,
        alpha=0.7,
        label="Training/validation data",
    )
    plt.plot(p_plot.numpy(), y_true_plot.numpy(), label="True function")
    plt.plot(p_plot.numpy(), y_pred_plot.numpy(), label="Network output")
    plt.xlabel("p")
    plt.ylabel("g(p)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "fit.png"), dpi=200)
    plt.close()


def plot_losses(
    save_dir: str,
    title: str,
    train_losses: list[float],
    val_losses: list[float],
) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "loss.png"), dpi=200)
    plt.close()


def run_experiment(config: ExperimentConfig, T: float = 4.0 / 3.0) -> dict:
    print(f"\n===== {config.name} =====")

    save_dir = os.path.join("plots", config.name.lower().replace(" ", "_"))
    os.makedirs(save_dir, exist_ok=True)

    p_raw, p_norm, y = make_dataset(
        num_points=config.num_points,
        T=T,
    )

    x_train, y_train, x_val, y_val = split_dataset(p_norm, y, config.training_ratio)

    model = SurrogateNet(hidden_dim=config.hidden_dim, activation=config.activation)

    train_losses, val_losses = train_model(
        model=model,
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        epochs=config.epochs,
        lr=config.lr,
    )

    model.eval()
    with torch.no_grad():
        y_train_pred = model(x_train)
        y_val_pred = model(x_val)

    train_metrics = compute_metrics(y_train, y_train_pred)
    val_metrics = compute_metrics(y_val, y_val_pred)

    print("Train Metrics:")
    print(
        f"  MSE={train_metrics['mse']:.6f}, "
        f"RMSE={train_metrics['rmse']:.6f}, "
        f"MAE={train_metrics['mae']:.6f}"
    )
    print("Validation Metrics:")
    print(
        f"  MSE={val_metrics['mse']:.6f}, "
        f"RMSE={val_metrics['rmse']:.6f}, "
        f"MAE={val_metrics['mae']:.6f}"
    )

    p_plot = torch.linspace(0.0, T, 400).unsqueeze(1)
    p_plot_norm = normalize_to_minus1_1(p_plot, 0.0, T)
    y_true_plot = target_function(p_plot)

    with torch.no_grad():
        y_pred_plot = model(p_plot_norm)

    plot_fit(
        save_dir=save_dir,
        title=f"{config.name}: Network Output vs True Function",
        p_data=p_raw,
        y_data=y,
        p_plot=p_plot,
        y_true_plot=y_true_plot,
        y_pred_plot=y_pred_plot,
    )

    plot_losses(
        save_dir=save_dir,
        title=f"{config.name}: Training and Validation Loss",
        train_losses=train_losses,
        val_losses=val_losses,
    )

    return {
        "config": config,
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
    }


def main() -> None:
    """
    Recommended setup for the assignment:

    1. Underfitting:
       - very small hidden layer
       - limited epochs
       - full dense dataset

    2. Good Fit:
       - moderate hidden layer
       - enough epochs
       - full dense dataset

    3. Overfitting:
       - large hidden layer
       - many epochs
       - very small dataset
       This makes overfitting actually visible.
    """
    experiments = [
        ExperimentConfig(
            name="Underfitting",
            hidden_dim=16,
            epochs=500,
            lr=1e-3,
            num_points=512,
            activation="tanh",
            training_ratio=0.8,
        ),
        ExperimentConfig(
            name="Good Fit",
            hidden_dim=64,
            epochs=5000,
            lr=1e-3,
            num_points=512,
            activation="tanh",
            training_ratio=0.8,
        ),
        ExperimentConfig(
            name="Overfitting",
            hidden_dim=128,
            epochs=5000,
            lr=1e-3,
            num_points=512,
            activation="tanh",
            training_ratio=0.2,
        ),
    ]

    results = []
    for config in experiments:
        result = run_experiment(config)
        results.append(result)

    print("\n===== Summary =====")
    for result in results:
        cfg = result["config"]
        val = result["val_metrics"]
        print(
            f"{cfg.name:12s} | "
            f"N={cfg.hidden_dim:<3d} | "
            f"points={cfg.num_points:<3d} | "
            f"Val MSE={val['mse']:.6f} | "
            f"Val RMSE={val['rmse']:.6f} | "
            f"Val MAE={val['mae']:.6f}"
        )


if __name__ == "__main__":
    main()
