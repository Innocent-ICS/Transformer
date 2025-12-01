# Bidirectional Translation Analysis

## Current Model Training Direction

After investigating the trained translation model, here's what we found:

### Training Configuration
- **Source Language**: Shona (vocabulary: 1,950 tokens)
- **Target Language**: English (vocabulary: 2,249 tokens)
- **Direction Trained**: Shona → English

### What This Means

1. **Shona → English (sn2en)**: ✅ **Works Well**
   - This is the direction the model was trained on
   - The model has learned to encode Shona and decode into English
   
2. **English → Shona (en2sn)**: ⚠️ **Limited Performance**
   - The model was NOT trained for this direction
   - Using the same weights in reverse will produce poor results
   - The encoder was trained on Shona features, decoder on English patterns

## How to Enable True Bidirectional Translation

To support both directions equally well, you have **two options**:

### Option 1: Train Two Separate Models
- Train one model: English → Shona
- Train another model: Shona → English  
- Use the appropriate model for each direction

### Option 2: Train a Single Bidirectional Model
Augment the dataset to include both directions by:
1. Creating two entries for each sentence pair:
   - Entry 1: (English source, Shona target)
   - Entry 2: (Shona source, English target)
2. Add a special token to indicate translation direction
3. Train one model on this augmented dataset

## Current Demonstration

The current model (`translation-final_best.pth.tar`) is optimized for **Shona → English** translation.

For production use:
- **Shona to English**: Use the current model
- **English to Shona**: Would require training a new model or using Option 2 above

## Technical Details

The Transformer architecture itself IS bidirectional-capable - it's just that:
- The **training data direction** determines what the model learns
- The **encoder** learns features specific to the source language
- The **decoder** learns generation patterns specific to the target language
- Reversing these roles requires retraining
