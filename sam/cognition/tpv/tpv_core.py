"""
TPV Core Module
Phase 0 - Core Installation

Core TPV (Thinking Process Verification) implementation for SAM.
This module provides the foundational infrastructure for meta-cognitive reasoning.
"""

import logging
import threading
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import json

from .tpv_config import TPVConfig

logger = logging.getLogger(__name__)

class TPVAttention(nn.Module):
    """Multi-head attention mechanism for TPV."""
    
    def __init__(self, hidden_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        assert self.head_dim * num_heads == hidden_dim, "hidden_dim must be divisible by num_heads"
        
        self.query = nn.Linear(hidden_dim, hidden_dim)
        self.key = nn.Linear(hidden_dim, hidden_dim)
        self.value = nn.Linear(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.output_proj = nn.Linear(hidden_dim, hidden_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        # Compute Q, K, V
        q = self.query(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.key(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.value(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn_weights = torch.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        attn_output = torch.matmul(attn_weights, v)
        attn_output = attn_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.hidden_dim
        )
        
        return self.output_proj(attn_output)

class TPVProcessor(nn.Module):
    """Core TPV processing module."""
    
    def __init__(self, config: TPVConfig):
        super().__init__()
        self.config = config
        self.hidden_dim = config.get_hidden_dimension()
        
        # TPV components
        self.attention = TPVAttention(
            hidden_dim=self.hidden_dim,
            num_heads=config.tpv_params.num_heads,
            dropout=config.tpv_params.dropout
        )
        
        self.norm1 = nn.LayerNorm(self.hidden_dim)
        self.norm2 = nn.LayerNorm(self.hidden_dim)
        
        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim * 4),
            nn.GELU() if config.tpv_params.activation == 'gelu' else nn.ReLU(),
            nn.Dropout(config.tpv_params.dropout),
            nn.Linear(self.hidden_dim * 4, self.hidden_dim)
        )
        
        # Meta-cognitive components
        self.confidence_head = nn.Linear(self.hidden_dim, 1)
        self.reasoning_quality_head = nn.Linear(self.hidden_dim, 1)
        
    def forward(self, hidden_states: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass through TPV processor.
        
        Args:
            hidden_states: Input hidden states [batch_size, seq_len, hidden_dim]
            
        Returns:
            Dictionary containing TPV outputs
        """
        # Self-attention with residual connection
        attn_output = self.attention(hidden_states)
        hidden_states = self.norm1(hidden_states + attn_output)
        
        # Feed-forward with residual connection
        ffn_output = self.ffn(hidden_states)
        hidden_states = self.norm2(hidden_states + ffn_output)
        
        # Meta-cognitive analysis
        # Use the last token's representation for global analysis
        last_hidden = hidden_states[:, -1, :]  # [batch_size, hidden_dim]
        
        confidence_score = torch.sigmoid(self.confidence_head(last_hidden))
        reasoning_quality = torch.sigmoid(self.reasoning_quality_head(last_hidden))
        
        return {
            'processed_states': hidden_states,
            'confidence_score': confidence_score,
            'reasoning_quality': reasoning_quality,
            'attention_output': attn_output
        }

class TPVCore:
    """Core TPV system for SAM."""

    # Class-level cache for initialized processors
    _processor_cache = {}
    _cache_lock = threading.Lock()

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize TPV Core.

        Args:
            config_path: Path to TPV configuration file
        """
        self.config = TPVConfig(config_path)
        self.processor = None
        self.device = self.config.get_device()
        self.is_initialized = False
        self._cache_key = self._generate_cache_key()

        logger.info(f"TPV Core initialized with device: {self.device}")

    def _generate_cache_key(self) -> str:
        """Generate cache key based on configuration."""
        config_dict = self.config.to_dict()
        # Create a hash of the configuration for caching
        import hashlib
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    def initialize(self) -> bool:
        """Initialize TPV processor and load assets with caching.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check cache first
            with self._cache_lock:
                if self._cache_key in self._processor_cache:
                    cached_processor, cached_device = self._processor_cache[self._cache_key]
                    if cached_device == self.device:
                        logger.info(f"🚀 Using cached TPV processor for {self.device}")
                        self.processor = cached_processor
                        self.is_initialized = True
                        return True

            logger.info("🔧 Initializing TPV processor...")

            # Validate configuration
            if not self.config.validate_config():
                logger.error("TPV configuration validation failed")
                return False

            # Initialize processor
            self.processor = TPVProcessor(self.config)

            # Move to device
            if self.device != 'cpu':
                try:
                    self.processor = self.processor.to(self.device)
                    logger.info(f"✅ TPV processor moved to {self.device}")
                except Exception as e:
                    logger.warning(f"Failed to move to {self.device}, using CPU: {e}")
                    self.device = 'cpu'

            # Load mock weights for Phase 0
            self._load_mock_weights()

            # Cache the initialized processor
            with self._cache_lock:
                self._processor_cache[self._cache_key] = (self.processor, self.device)
                logger.info(f"📦 Cached TPV processor for future use")

            self.is_initialized = True
            logger.info("✅ TPV Core initialization completed")
            return True

        except Exception as e:
            logger.error(f"TPV initialization failed: {e}")
            return False
    
    def _load_mock_weights(self):
        """Load mock weights for Phase 0 development."""
        try:
            assets_dir = Path(__file__).parent.parent.parent / "assets" / "tpv"
            config_path = assets_dir / "tpv_model_config.json"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    asset_config = json.load(f)
                
                if asset_config.get('mock', False):
                    logger.info("🔧 Using mock weights for Phase 0 development")
                    # Initialize with random weights (mock)
                    for param in self.processor.parameters():
                        if param.dim() > 1:
                            nn.init.xavier_uniform_(param)
                        else:
                            nn.init.zeros_(param)
                else:
                    logger.info("📦 Loading production weights")
                    # In future phases, load actual pre-trained weights here
            
        except Exception as e:
            logger.warning(f"Weight loading failed, using random initialization: {e}")
    
    def process_thinking(self, hidden_states: torch.Tensor) -> Dict[str, Any]:
        """Process thinking states through TPV.
        
        Args:
            hidden_states: Hidden states from the main model
            
        Returns:
            TPV analysis results
        """
        if not self.is_initialized:
            logger.error("TPV not initialized. Call initialize() first.")
            return {}
        
        try:
            self.processor.eval()
            with torch.no_grad():
                # Ensure input is on correct device
                if hidden_states.device != torch.device(self.device):
                    hidden_states = hidden_states.to(self.device)
                
                # Process through TPV
                results = self.processor(hidden_states)
                
                # Convert to CPU and extract values
                output = {
                    'confidence_score': float(results['confidence_score'].cpu().item()),
                    'reasoning_quality': float(results['reasoning_quality'].cpu().item()),
                    'processed_states': results['processed_states'].cpu(),
                    'meta_analysis': {
                        'thinking_coherence': float(results['confidence_score'].cpu().item()),
                        'reasoning_depth': float(results['reasoning_quality'].cpu().item()),
                        'processing_status': 'completed'
                    }
                }
                
                return output
                
        except Exception as e:
            logger.error(f"TPV processing failed: {e}")
            return {
                'confidence_score': 0.5,
                'reasoning_quality': 0.5,
                'meta_analysis': {
                    'thinking_coherence': 0.5,
                    'reasoning_depth': 0.5,
                    'processing_status': 'error',
                    'error': str(e)
                }
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get TPV system status.
        
        Returns:
            Status information dictionary
        """
        return {
            'initialized': self.is_initialized,
            'device': self.device,
            'config': self.config.to_dict(),
            'phase': "Phase 0 - Core Installation",
            'version': "0.1.0"
        }
    
    def __str__(self) -> str:
        """String representation of TPV Core."""
        status = "initialized" if self.is_initialized else "not initialized"
        return f"TPVCore({status}, device={self.device})"
