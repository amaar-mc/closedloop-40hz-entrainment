#!/usr/bin/env python3
"""
Quick runner script for improved training (Version 2)

This script trains the enhanced EEGNetV2 model with:
- ΔPAC prediction (change, not absolute)
- Data augmentation
- Shorter prediction horizon (0.5s)
- Huber loss + improved training

Expected improvement: R² = 0.084 → 0.30+ (target)

Usage:
    python run_training_v2.py

Author: Amaar Chughtai
Date: February 2026
"""

import sys
sys.path.insert(0, 'src')

from training_v2 import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("IMPROVED TRAINING PIPELINE (Version 2)")
    print("="*80)
    print("\nKey Improvements:")
    print("  ✓ ΔPAC prediction (change vs absolute)")
    print("  ✓ Shorter prediction horizon (0.5s vs 1s)")
    print("  ✓ Data augmentation (time jitter, scaling, noise)")
    print("  ✓ Enhanced EEGNet (F1=12, F2=24, ~3200 params)")
    print("  ✓ Huber loss (robust to outliers)")
    print("  ✓ Cosine annealing learning rate")
    print("  ✓ Gradient clipping")
    print("  ✓ Longer training (150 epochs, patience=20)")
    print("\nTarget: R² > 0.30 (currently 0.084)")
    print("="*80 + "\n")

    input("Press Enter to start training (or Ctrl+C to cancel)...")

    main()
