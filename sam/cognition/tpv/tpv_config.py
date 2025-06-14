"""
TPV Configuration Management
Phase 0 - Core Installation

Handles configuration loading and validation for TPV module.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelParams:
    """Model parameters configuration."""
    hidden_dimension: int
    model_name: str
    architecture: str
    discovered_at: str

@dataclass
class TPVParams:
    """TPV-specific parameters."""
    num_heads: int
    dropout: float
    activation: str

@dataclass
class RuntimeParams:
    """Runtime configuration parameters."""
    device: str
    dtype: str
    batch_size: int

@dataclass
class ControlParams:
    """Active control configuration parameters."""
    completion_threshold: float
    plateau_threshold: float
    plateau_patience: int
    max_tokens: int
    min_steps: int

class TPVConfig:
    """TPV Configuration manager."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize TPV configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "tpv_config.yaml"
        
        self.config_path = config_path
        self._config_data = None
        self._model_params = None
        self._tpv_params = None
        self._runtime_params = None
        self._control_params = None

        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file.
        
        Returns:
            True if configuration loaded successfully, False otherwise.
        """
        try:
            if not self.config_path.exists():
                logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                self._config_data = yaml.safe_load(f)
            
            # Parse configuration sections
            self._parse_model_params()
            self._parse_tpv_params()
            self._parse_runtime_params()
            self._parse_control_params()
            
            logger.info(f"✅ TPV configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load TPV configuration: {e}")
            return False
    
    def _parse_model_params(self):
        """Parse model parameters from configuration."""
        model_data = self._config_data.get('model_params', {})
        self._model_params = ModelParams(
            hidden_dimension=model_data.get('hidden_dimension', 4096),
            model_name=model_data.get('model_name', ''),
            architecture=model_data.get('architecture', ''),
            discovered_at=model_data.get('discovered_at', '')
        )
    
    def _parse_tpv_params(self):
        """Parse TPV parameters from configuration."""
        tpv_data = self._config_data.get('tpv_params', {})
        self._tpv_params = TPVParams(
            num_heads=tpv_data.get('num_heads', 8),
            dropout=tpv_data.get('dropout', 0.1),
            activation=tpv_data.get('activation', 'gelu')
        )
    
    def _parse_runtime_params(self):
        """Parse runtime parameters from configuration."""
        runtime_data = self._config_data.get('runtime_params', {})
        self._runtime_params = RuntimeParams(
            device=runtime_data.get('device', 'auto'),
            dtype=runtime_data.get('dtype', 'float32'),
            batch_size=runtime_data.get('batch_size', 1)
        )

    def _parse_control_params(self):
        """Parse control parameters from configuration."""
        control_data = self._config_data.get('control_params', {})
        self._control_params = ControlParams(
            completion_threshold=control_data.get('completion_threshold', 0.92),
            plateau_threshold=control_data.get('plateau_threshold', 0.005),
            plateau_patience=control_data.get('plateau_patience', 3),
            max_tokens=control_data.get('max_tokens', 500),
            min_steps=control_data.get('min_steps', 2)
        )
    
    @property
    def model_params(self) -> ModelParams:
        """Get model parameters."""
        return self._model_params
    
    @property
    def tpv_params(self) -> TPVParams:
        """Get TPV parameters."""
        return self._tpv_params
    
    @property
    def runtime_params(self) -> RuntimeParams:
        """Get runtime parameters."""
        return self._runtime_params

    @property
    def control_params(self) -> ControlParams:
        """Get control parameters."""
        return self._control_params
    
    def get_hidden_dimension(self) -> int:
        """Get the model hidden dimension."""
        return self._model_params.hidden_dimension
    
    def get_device(self) -> str:
        """Get the target device for computation with GPU acceleration support."""
        device = self._runtime_params.device
        if device == 'auto':
            try:
                import torch
                if torch.cuda.is_available():
                    # Use the current CUDA device
                    return f'cuda:{torch.cuda.current_device()}'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    # Apple Silicon GPU support
                    return 'mps'
                else:
                    return 'cpu'
            except ImportError:
                return 'cpu'
        return device

    def get_torch_device(self):
        """Get PyTorch device object for tensor operations."""
        try:
            import torch
            device_str = self.get_device()
            return torch.device(device_str)
        except ImportError:
            return None
    
    def validate_config(self) -> bool:
        """Validate configuration completeness and correctness.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        try:
            # Check required parameters
            if self._model_params.hidden_dimension <= 0:
                logger.error("Invalid hidden dimension")
                return False
            
            if self._tpv_params.num_heads <= 0:
                logger.error("Invalid number of attention heads")
                return False
            
            if not (0.0 <= self._tpv_params.dropout <= 1.0):
                logger.error("Invalid dropout value")
                return False
            
            logger.info("✅ TPV configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary.
        """
        return {
            'model_params': {
                'hidden_dimension': self._model_params.hidden_dimension,
                'model_name': self._model_params.model_name,
                'architecture': self._model_params.architecture,
                'discovered_at': self._model_params.discovered_at
            },
            'tpv_params': {
                'num_heads': self._tpv_params.num_heads,
                'dropout': self._tpv_params.dropout,
                'activation': self._tpv_params.activation
            },
            'runtime_params': {
                'device': self._runtime_params.device,
                'dtype': self._runtime_params.dtype,
                'batch_size': self._runtime_params.batch_size
            }
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"TPVConfig(hidden_dim={self.get_hidden_dimension()}, device={self.get_device()})"
