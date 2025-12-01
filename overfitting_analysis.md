# Overfitting Analysis

## Problem
The training shows classic overfitting behavior:
- **Translation**: Train loss decreases from ~5.5 to ~3.8, but validation loss increases from ~5.3 to ~5.5
- **Generation**: Train loss decreases from ~4.7 to ~2.3, but validation loss increases from ~4.7 to ~5.5

## Root Causes
1. **Small Dataset**: Only 997 training samples (with 20% validation split = ~797 train, 200 val)
2. **Large Model**: d_model=512, 6 layers, 8 heads = millions of parameters
3. **Parameter Count Mismatch**: Model capacity >> data size
4. **Insufficient Regularization**: Only dropout=0.1

## Proposed Fixes
1. **Reduce Model Size**: d_model=256, n_layers=3, heads=4
2. **Increase Dropout**: dropout=0.3
3. **Add Label Smoothing**: smoothing=0.1
4. **Lower Learning Rate**: lr=0.0001 (was 0.0005)
5. **Reduce Batch Size**: batch_size=16 (was 32) for better generalization

## Implementation
Updating training scripts with new hyperparameters.
