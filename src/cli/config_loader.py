"""
Configuration loader for OPRLM batch downloader.

Uses the existing YAML parser from utils.yaml_parser to load
PdbFileOptionRequest objects from YAML files.
"""

from pathlib import Path
from typing import Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_parser import load_yaml_config
from api.models import PdbFileOptionRequest


class ConfigLoader:
    """Loads YAML configuration files using the existing parser."""
    
    def __init__(self, input_dir: Path, config_pattern: str = "*.yml"):
        """
        Initialize the config loader.
        
        Args:
            input_dir: Directory containing YAML configuration files
            config_pattern: File pattern for YAML configs (default: *.yml)
        """
        self.input_dir = input_dir
        self.config_pattern = config_pattern
    
    def load_configs(self) -> Dict[Path, PdbFileOptionRequest]:
        """
        Load all YAML configuration files from the input directory.
        
        Returns:
            Dictionary mapping config file paths to PdbFileOptionRequest objects
            
        Raises:
            FileNotFoundError: If input directory doesn't exist
            ValueError: If no config files are found
        """
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")
        
        config_files = list(self.input_dir.glob(self.config_pattern))
        
        if not config_files:
            raise ValueError(f"No configuration files found matching pattern: {self.config_pattern}")
        
        configs = {}
        for config_file in config_files:
            try:
                config = load_yaml_config(str(config_file))
                configs[config_file] = config
            except Exception as e:
                raise ValueError(f"Failed to load config {config_file}: {e}")
        
        return configs
    
    def validate_configs(self, configs: Dict[Path, PdbFileOptionRequest]) -> Dict[Path, str]:
        """
        Validate loaded configurations.
        
        Args:
            configs: Dictionary of loaded configurations
            
        Returns:
            Dictionary mapping config paths to validation error messages
            (empty if all configs are valid)
        """
        errors = {}
        
        for config_path, config in configs.items():
            try:
                # Basic validation
                if not config.pdb_id:
                    errors[config_path] = "Missing pdb_id"
                elif not config.file_input_mode:
                    errors[config_path] = "Missing file_input_mode"
                elif config.file_input_mode.value == "upload" and not config.file_path:
                    errors[config_path] = "file_path required for CUSTOM upload mode"
                elif config.file_path and not config.file_path.exists():
                    errors[config_path] = f"File not found: {config.file_path}"
                    
            except Exception as e:
                errors[config_path] = str(e)
        
        return errors