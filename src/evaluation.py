"""
Performance Evaluation Module
Runs all strategies, compares metrics, and generates plots + CSV.
"""

from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import config
from src.simulation import Simulation


def run_comparison(strategies: List[str] = None) -> pd.DataFrame:
    if strategies is None:
        strategies = config.BASELINES

    all_results = []
    for strat in strategies:
        sim = Simulation(strategy=strat)
        result = sim.run()
        all_results.append(result)

    df = pd.DataFrame(all_results)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(config.RESULTS_DIR, "comparison_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")
    return df


def plot_results(df: pd.DataFrame):
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    sns.set_theme(style="whitegrid")

    metrics = [
        ("packet_delivery_ratio", "Packet Delivery Ratio"),
        ("avg_latency", "Average Latency (s)"),
        ("total_energy", "Total Energy Consumption"),
        ("load_fairness", "Load Fairness (Jain's Index)"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, (col, title) in zip(axes, metrics):
        sns.barplot(data=df, x="strategy", y=col, ax=ax, palette="viridis")
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel(title)

    plt.tight_layout()
    plot_path = os.path.join(config.RESULTS_DIR, "performance_comparison.png")
    plt.savefig(plot_path, dpi=150)
    print(f"Plot saved to {plot_path}")
    plt.close()


def print_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60)