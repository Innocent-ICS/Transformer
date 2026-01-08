"""
Generation service using the Language Model.
"""
import torch
from typing import Dict, Any
import time


class GenerationService:
    """Service for generating text using loaded models"""
    
    def __init__(self, registry):
        self.registry = registry
    
    def generate(
        self,
        prompt: str,
        model_id: str,
        max_length: int = 100,
        temperature: float = 0.8
    ) -> Dict[str, Any]:
        """
        Generate text from a prompt using the specified model.
        
        Args:
            prompt: Input prompt
            model_id: ID of the generation model to use
            max_length: Maximum length to generate
            temperature: Sampling temperature (higher = more random)
            
        Returns:
            Dictionary with generated text and metadata
        """
        start_time = time.time()
        
        # Get model and tokenizer
        model = self.registry.get_model(model_id)
        tokenizer = self.registry.get_tokenizers(model_id)
        device = self.registry.device
        
        # Tokenize prompt
        tokens = tokenizer.encode(prompt)
        input_ids = torch.tensor([tokens], dtype=torch.long).to(device)
        
        generated = tokens.copy()
        
        with torch.no_grad():
            for _ in range(max_length):
                # Create causal mask
                size = input_ids.size(1)
                mask = torch.triu(torch.ones(size, size), diagonal=1).type_as(input_ids).float().unsqueeze(0).unsqueeze(0) == 0
                pad_mask = (input_ids != 0).unsqueeze(1).unsqueeze(2)
                mask = mask & pad_mask
                
                # Get predictions
                output = model(input_ids, mask)
                
                # Get next token probabilities (last position)
                logits = output[:, -1, :] / temperature
                probs = torch.softmax(logits, dim=-1)
                
                # Sample from distribution
                next_token = torch.multinomial(probs, num_samples=1).item()
                
                # Stop if we hit EOS
                if next_token == tokenizer.eos_token_id:
                    break
                
                generated.append(next_token)
                
                # Update input (use sliding window if too long)
                if len(generated) > 512:
                    input_ids = torch.tensor([generated[-512:]], dtype=torch.long).to(device)
                else:
                    input_ids = torch.tensor([generated], dtype=torch.long).to(device)
        
        generated_text = tokenizer.decode(generated, skip_special_tokens=True)
        inference_time = int((time.time() - start_time) * 1000)  # milliseconds
        
        return {
            'generated_text': generated_text,
            'model_used': model_id,
            'prompt': prompt,
            'temperature': temperature,
            'max_length': max_length,
            'inference_time_ms': inference_time
        }
