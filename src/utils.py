"""
Utility Functions for Closed-Loop 40Hz Entrainment Project

This module provides helper functions for:
- Configuration management
- Logging setup
- Plotting utilities
- Metrics computation
- File I/O operations

Author: Amaar Chughtai
Date: February 2026
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    """
    Configure logging for the project.

    Args:
        log_file: Path to log file. If None, only console logging
        level: Logging level (default: INFO)

    Returns:
        logger: Configured logger object
    """
    logger = logging.getLogger('closed_loop_entrainment')
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_config(config_path: str) -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config.yaml

    Returns:
        config: Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_config(config: Dict, output_path: str):
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        output_path: Path to save config
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def save_metrics(metrics: Dict, output_path: str):
    """
    Save metrics dictionary to JSON file.

    Args:
        metrics: Metrics dictionary
        output_path: Path to save metrics
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute regression evaluation metrics.

    Args:
        y_true: Ground truth values (N,)
        y_pred: Predicted values (N,)

    Returns:
        metrics: Dictionary with MSE, RMSE, MAE, R^2
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Pearson correlation
    correlation = np.corrcoef(y_true, y_pred)[0, 1]

    return {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2),
        'correlation': float(correlation)
    }


def plot_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray,
                           title: str = "PAC Prediction Accuracy",
                           save_path: Optional[str] = None):
    """
    Create scatter plot comparing predicted vs actual PAC values.

    Args:
        y_true: Ground truth PAC values
        y_pred: Predicted PAC values
        title: Plot title
        save_path: Path to save figure (if None, display only)
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.5, s=20, c='blue', edgecolors='none')

    # Identity line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')

    # Compute metrics
    metrics = compute_regression_metrics(y_true, y_pred)

    # Add metrics text
    textstr = f"R² = {metrics['r2']:.3f}\n"
    textstr += f"RMSE = {metrics['rmse']:.4f}\n"
    textstr += f"MAE = {metrics['mae']:.4f}\n"
    textstr += f"Corr = {metrics['correlation']:.3f}"

    ax.text(0.05, 0.95, textstr, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('Actual PAC', fontsize=13)
    ax.set_ylabel('Predicted PAC', fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()

    plt.close()


def plot_pac_timeseries(time: np.ndarray, pac_values: np.ndarray,
                       stimulation: Optional[np.ndarray] = None,
                       title: str = "PAC Time Series",
                       save_path: Optional[str] = None):
    """
    Plot PAC values over time with optional stimulation markers.

    Args:
        time: Time vector (seconds)
        pac_values: PAC values over time
        stimulation: Binary stimulation state (1=ON, 0=OFF) or None
        title: Plot title
        save_path: Path to save figure
    """
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Plot PAC
    ax1.plot(time, pac_values, 'b-', lw=2, label='PAC')
    ax1.set_xlabel('Time (s)', fontsize=13)
    ax1.set_ylabel('Phase-Amplitude Coupling', color='b', fontsize=13)
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, alpha=0.3)

    # Plot stimulation if provided
    if stimulation is not None:
        ax2 = ax1.twinx()
        ax2.fill_between(time, 0, stimulation, alpha=0.3, color='orange',
                         label='Stimulation', step='post')
        ax2.set_ylabel('Stimulation (ON/OFF)', color='orange', fontsize=13)
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['OFF', 'ON'])
        ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_title(title, fontsize=14, fontweight='bold')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    if stimulation is not None:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    else:
        ax1.legend(loc='upper right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()

    plt.close()


def plot_training_curves(train_losses: List[float], val_losses: List[float],
                         title: str = "Training Curves",
                         save_path: Optional[str] = None):
    """
    Plot training and validation loss curves.

    Args:
        train_losses: Training loss per epoch
        val_losses: Validation loss per epoch
        title: Plot title
        save_path: Path to save figure
    """
    epochs = np.arange(1, len(train_losses) + 1)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(epochs, train_losses, 'b-', lw=2, label='Training Loss')
    ax.plot(epochs, val_losses, 'r-', lw=2, label='Validation Loss')

    # Mark best epoch
    best_epoch = np.argmin(val_losses) + 1
    best_val_loss = val_losses[best_epoch - 1]
    ax.axvline(best_epoch, color='green', linestyle='--', lw=1.5,
               label=f'Best Epoch: {best_epoch}')
    ax.plot(best_epoch, best_val_loss, 'go', markersize=10)

    ax.set_xlabel('Epoch', fontsize=13)
    ax.set_ylabel('Loss (MSE)', fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)

    # Annotate best value
    ax.annotate(f'Val Loss: {best_val_loss:.4f}',
                xy=(best_epoch, best_val_loss),
                xytext=(best_epoch + 5, best_val_loss + 0.001),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()

    plt.close()


def plot_comparison_bars(metrics_dict: Dict[str, Dict[str, float]],
                         metric_name: str = "PAC Improvement (%)",
                         title: str = "Method Comparison",
                         save_path: Optional[str] = None):
    """
    Create bar plot comparing multiple methods.

    Args:
        metrics_dict: {method_name: {metric: value}}
        metric_name: Name of metric to plot
        title: Plot title
        save_path: Path to save figure
    """
    methods = list(metrics_dict.keys())
    values = [metrics_dict[m][metric_name] for m in methods]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['gray', 'lightcoral', 'skyblue', 'orange', 'green']
    bars = ax.bar(methods, values, color=colors[:len(methods)], alpha=0.8, edgecolor='black')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel(metric_name, fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Rotate x labels if needed
    plt.xticks(rotation=15, ha='right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    else:
        plt.show()

    plt.close()


def save_results_csv(results: Dict[str, any], output_path: str):
    """
    Save results dictionary to CSV file.

    Args:
        results: Results dictionary (supports nested dicts)
        output_path: Path to save CSV
    """
    # Flatten nested dictionaries
    flat_results = {}
    for key, value in results.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_results[f"{key}_{sub_key}"] = sub_value
        else:
            flat_results[key] = value

    # Convert to DataFrame
    df = pd.DataFrame([flat_results])

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved results to {output_path}")


def ensure_dir(directory: Union[str, Path]):
    """
    Create directory if it doesn't exist.

    Args:
        directory: Path to directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_device(use_cuda: bool = True) -> str:
    """
    Get PyTorch device (cuda or cpu).

    Args:
        use_cuda: Whether to use CUDA if available

    Returns:
        device: 'cuda' or 'cpu'
    """
    import torch
    if use_cuda and torch.cuda.is_available():
        device = 'cuda'
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("Using CPU")
    return device


def count_parameters(model) -> int:
    """
    Count trainable parameters in a PyTorch model.

    Args:
        model: PyTorch model

    Returns:
        count: Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def print_model_summary(model, input_shape: Tuple):
    """
    Print model architecture summary.

    Args:
        model: PyTorch model
        input_shape: Input tensor shape (without batch dimension)
    """
    import torch
    from torchsummary import summary
    try:
        summary(model, input_shape)
    except:
        print(f"Model: {model.__class__.__name__}")
        print(f"Parameters: {count_parameters(model):,}")


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")

    # Test logging
    logger = setup_logging(log_file="logs/test.log")
    logger.info("Logging test successful")

    # Test metrics
    y_true = np.random.rand(100) * 0.3
    y_pred = y_true + np.random.randn(100) * 0.05
    metrics = compute_regression_metrics(y_true, y_pred)
    print(f"\nRegression Metrics: {metrics}")

    # Test plotting
    plot_prediction_scatter(y_true, y_pred, save_path=None)

    print("\nAll utility tests passed!")
