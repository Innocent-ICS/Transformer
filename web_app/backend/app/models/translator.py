"""
Translation service using the Transformer model.
"""
import torch
from typing import Dict, Any
import time


class TranslationService:
    """Service for translating text using loaded models"""
    
    def __init__(self, registry):
        self.registry = registry
    
    def translate(
        self,
        text: str,
        model_id: str,
        max_length: int = 100
    ) -> Dict[str, Any]:
        """
        Translate text using the specified model.
        
        Args:
            text: Source text to translate
            model_id: ID of the translation model to use
            max_length: Maximum length of translation
            
        Returns:
            Dictionary with translation and metadata
        """
        start_time = time.time()
        
        # Get model and tokenizers
        model = self.registry.get_model(model_id)
        tokenizers = self.registry.get_tokenizers(model_id)
        src_tokenizer = tokenizers['src']
        trg_tokenizer = tokenizers['trg']
        
        device = self.registry.device
        
        # Encode source text
        src_ids = torch.LongTensor([src_tokenizer.encode(text)]).to(device)
        src_mask = (src_ids != 0).unsqueeze(1).unsqueeze(2)
        
        # Encode
        with torch.no_grad():
            memory = model.encode(src_ids, src_mask)
        
        # Greedy decoding
        ys = torch.ones(1, 1).fill_(trg_tokenizer.sos_token_id).type_as(src_ids)
        
        for _ in range(max_length):
            with torch.no_grad():
                out = model.decode(
                    memory, src_mask, ys,
                    torch.triu(torch.ones(1, ys.size(1), ys.size(1), device=device), diagonal=1) == 0
                )
            
            prob = out[:, -1]
            _, next_word = torch.max(prob, dim=1)
            next_word = next_word.data[0]
            
            if next_word == trg_tokenizer.eos_token_id:
                break
            
            ys = torch.cat([ys, torch.ones(1, 1).type_as(src_ids).fill_(next_word)], dim=1)
        
        # Decode to text
        translation = trg_tokenizer.decode(ys[0].tolist(), skip_special_tokens=True)
        
        inference_time = int((time.time() - start_time) * 1000)  # milliseconds
        
        return {
            'translation': translation,
            'model_used': model_id,
            'inference_time_ms': inference_time,
            'source_text': text
        }
