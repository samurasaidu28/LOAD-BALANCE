#!/usr/bin/env python3
"""
Main entry point for the AI-Optimised Load-Balancing Framework
Group 13 - IPAM, University of Sierra Leone

Usage:
    python main.py                  # run full comparison
    python main.py --strategy ai    # run only AI strategy
"""

import argparse
import random
import numpy as np
import config
from src.evaluation import run_comparison, plot_results, print_summary
from src.simulation import Simulation


def set_seed(seed: int = config.RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)


def main():
    parser = argparse.ArgumentParser(description="AI Load-Balancing P2P Simulation")
    parser.add_argument(
        "--strategy",
        choices=["ai", "random", "round_robin", "all"],
        default="all",
        help="Which strategy to run",
    )
    args = parser.parse_args()

    set_seed()

    if args.strategy == "all":
        df = run_comparison()
        print_summary(df)
        plot_results(df)
    else:
        sim = Simulation(strategy=args.strategy)
        result = sim.run()
        print("\nFinal Result:")
        for k, v in result.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()