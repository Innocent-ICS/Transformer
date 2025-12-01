"""
Model Registry for managing multiple Transformer models.
Supports lazy loading and hot-swapping of models.
"""
import torch
import json
from typing import Dict, Optional, Any
from pathlib import Path
import sys

# Add parent directory to path to import model classes
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from model import make_model, make_lm_model
from text_data import Tokenizer


class ModelConfig:
    """Configuration for a single model"""
    def __init__(self, config_dict: Dict[str, Any]):
        self.model_id = config_dict['model_id']
        self.type = config_dict['type']  # 'translation' or 'generation'
        self.checkpoint_path = config_dict['checkpoint_path']
        self.config = config_dict['config']
        self.metadata = config_dict.get('metadata', {})
        self.tokenizer_config = config_dict.get('tokenizer_config', {})


class ModelRegistry:
    """Central registry for managing Transformer models"""
    
    def __init__(self, device: str = 'auto'):
        self.models: Dict[str, ModelConfig] = {}
        self.loaded_models: Dict[str, torch.nn.Module] = {}
        self.tokenizers: Dict[str, Any] = {}
        
        # Auto-detect device
        if device == 'auto':
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)
        
        print(f"ModelRegistry initialized on device: {self.device}")
    
    def register_model(self, config: Dict[str, Any]):
        """Register a model with its configuration"""
        model_config = ModelConfig(config)
        self.models[model_config.model_id] = model_config
        print(f"Registered model: {model_config.model_id} ({model_config.type})")
    
    def load_model(self, model_id: str) -> torch.nn.Module:
        """Load a model and its tokenizers"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        
        if model_id in self.loaded_models:
            print(f"Model {model_id} already loaded")
            return self.loaded_models[model_id]
        
        config = self.models[model_id]
        print(f"Loading model {model_id}...")
        
        # Load tokenizers first
        self._load_tokenizers(model_id, config)
        
        # Load model based on type
        if config.type == 'translation':
            model = self._load_translation_model(config)
        elif config.type == 'generation':
            model = self._load_generation_model(config)
        else:
            raise ValueError(f"Unknown model type: {config.type}")
        
        model.to(self.device)
        model.eval()
        
        self.loaded_models[model_id] = model
        print(f"Successfully loaded model {model_id}")
        
        return model
    
    def _load_tokenizers(self, model_id: str, config: ModelConfig):
        """Load tokenizers for the model"""
        tokenizer_config = config.tokenizer_config
        
        if config.type == 'translation':
            # Load source and target tokenizers
            src_tokenizer = Tokenizer(min_freq=tokenizer_config.get('min_freq', 2))
            trg_tokenizer = Tokenizer(min_freq=tokenizer_config.get('min_freq', 2))
            
            # Build vocabularies
            with open(tokenizer_config['src_vocab_file'], 'r') as f:
                src_tokenizer.build_vocab(f.readlines())
            with open(tokenizer_config['trg_vocab_file'], 'r') as f:
                trg_tokenizer.build_vocab(f.readlines())
            
            self.tokenizers[model_id] = {
                'src': src_tokenizer,
                'trg': trg_tokenizer
            }
        
        elif config.type == 'generation':
            # Load single tokenizer
            tokenizer = Tokenizer(min_freq=tokenizer_config.get('min_freq', 2))
            with open(tokenizer_config['vocab_file'], 'r') as f:
                tokenizer.build_vocab(f.readlines())
            
            self.tokenizers[model_id] = tokenizer
    
    def _load_translation_model(self, config: ModelConfig) -> torch.nn.Module:
        """Load a translation model"""
        model_config = config.config
        
        model = make_model(
            model_config['src_vocab_size'],
            model_config['trg_vocab_size'],
            N=model_config['n_layers'],
            d_model=model_config['d_model'],
            h=model_config['heads'],
            dropout=model_config['dropout']
        )
        
        # Load checkpoint
        checkpoint = torch.load(config.checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint['state_dict'])
        
        return model
    
    def _load_generation_model(self, config: ModelConfig) -> torch.nn.Module:
        """Load a generation model"""
        model_config = config.config
        
        model = make_lm_model(
            model_config['vocab_size'],
            N=model_config['n_layers'],
            d_model=model_config['d_model'],
            h=model_config['heads'],
            dropout=model_config['dropout']
        )
        
        # Load checkpoint
        checkpoint = torch.load(config.checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint['state_dict'])
        
        return model
    
    def unload_model(self, model_id: str):
        """Unload a model to free memory"""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            if model_id in self.tokenizers:
                del self.tokenizers[model_id]
            
            # Clear CUDA cache if using GPU
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            
            print(f"Unloaded model {model_id}")
    
    def get_model(self, model_id: str) -> torch.nn.Module:
        """Get a model, loading it if necessary"""
        if model_id not in self.loaded_models:
            self.load_model(model_id)
        return self.loaded_models[model_id]
    
    def get_tokenizers(self, model_id: str):
        """Get tokenizers for a model"""
        if model_id not in self.tokenizers:
            raise ValueError(f"Tokenizers for {model_id} not loaded")
        return self.tokenizers[model_id]
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all registered models with their metadata"""
        return {
            model_id: {
                'model_id': model_id,
                'type': config.type,
                'metadata': config.metadata,
                'loaded': model_id in self.loaded_models
            }
            for model_id, config in self.models.items()
        }
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        
        config = self.models[model_id]
        return {
            'model_id': model_id,
            'type': config.type,
            'metadata': config.metadata,
            'config': config.config,
            'loaded': model_id in self.loaded_models
        }
