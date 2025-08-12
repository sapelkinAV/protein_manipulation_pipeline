"""
YAML parser utility for PdbFileOptionRequest objects.

This module provides functionality to parse YAML configuration files
into PdbFileOptionRequest objects for use with the OPRLM selenium client.
YAML files use human-readable enum names instead of string values.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.models import PdbFileOptionRequest, MembraneConfig, IonConfiguration, MDInputOptions
from api.models import ProteinStructure, MembraneType, ProteinTopologyMembrane, IonType


class YamlConfigParser:
    """Parser for YAML configuration files to PdbFileOptionRequest objects."""
    
    @staticmethod
    def parse_yaml_file(yaml_path: Path) -> PdbFileOptionRequest:
        """
        Parse a YAML file into a PdbFileOptionRequest object.
        
        Args:
            yaml_path: Path to the YAML configuration file
            
        Returns:
            PdbFileOptionRequest object configured from YAML
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            yaml.YAMLError: If the YAML is malformed
            ValueError: If required fields are missing or invalid
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
            
        with open(yaml_path, 'r') as file:
            config_data = yaml.safe_load(file)
            
        return YamlConfigParser.parse_dict(config_data)
    
    @staticmethod
    def parse_yaml_string(yaml_string: str) -> PdbFileOptionRequest:
        """
        Parse a YAML string into a PdbFileOptionRequest object.
        
        Args:
            yaml_string: YAML configuration as a string
            
        Returns:
            PdbFileOptionRequest object configured from YAML
            
        Raises:
            yaml.YAMLError: If the YAML is malformed
            ValueError: If required fields are missing or invalid
        """
        config_data = yaml.safe_load(yaml_string)
        return YamlConfigParser.parse_dict(config_data)
    
    @staticmethod
    def parse_dict(config_data: Dict[str, Any]) -> PdbFileOptionRequest:
        """
        Parse a dictionary into a PdbFileOptionRequest object.
        
        Args:
            config_data: Dictionary containing configuration data
            
        Returns:
            PdbFileOptionRequest object configured from dictionary
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Helper function to get enum from name
        def get_enum_by_name(enum_class, name, default=None):
            try:
                return enum_class[name]
            except KeyError:
                if default is not None:
                    return default
                raise ValueError(f"Invalid {enum_class.__name__}: {name}")
        
        # Validate required fields
        required_fields = ['pdb_id', 'file_input_mode']
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"Required field '{field}' is missing from YAML configuration")
        
        # Parse membrane configuration
        membrane_config_data = config_data.get('membrane_config', {})
        membrane_type_name = membrane_config_data.get('membrane_type', 'CUSTOM')
        protein_topology_name = membrane_config_data.get('protein_topology', 'IN')
        
        membrane_config = MembraneConfig(
            membrane_type=get_enum_by_name(MembraneType, membrane_type_name),
            popc=membrane_config_data.get('popc', True),
            dopc=membrane_config_data.get('dopc', False),
            dspc=membrane_config_data.get('dspc', False),
            dmpc=membrane_config_data.get('dmpc', False),
            dppc=membrane_config_data.get('dppc', False),
            chol_value=membrane_config_data.get('chol_value', 20.0),
            protein_topology=get_enum_by_name(ProteinTopologyMembrane, protein_topology_name)
        )
        
        # Parse ion configuration
        ion_config_data = config_data.get('ion_configuration', {})
        ion_type_name = ion_config_data.get('ion_type', 'KCl')
        
        ion_configuration = IonConfiguration(
            ion_concentration=ion_config_data.get('ion_concentration', 0.15),
            ion_type=get_enum_by_name(IonType, ion_type_name)
        )
        
        # Parse file input mode
        file_input_mode_name = config_data['file_input_mode']
        file_input_mode = get_enum_by_name(ProteinStructure, file_input_mode_name)
        
        # Handle file path
        file_path = None
        if 'file_path' in config_data and config_data['file_path']:
            file_path = Path(config_data['file_path'])
            
        # Handle output path
        output_path = None
        if 'output_path' in config_data and config_data['output_path']:
            output_path = Path(config_data['output_path'])
        
        # Parse MD input options
        md_options_data = config_data.get('md_input_options', {})
        md_input_options = MDInputOptions(
            namd_enabled=md_options_data.get('namd_enabled', False),
            gromacs_enabled=md_options_data.get('gromacs_enabled', True),
            openmm_enabled=md_options_data.get('openmm_enabled', True)
        )
        
        # Create PdbFileOptionRequest
        return PdbFileOptionRequest(
            pdb_id=config_data['pdb_id'],
            file_input_mode=file_input_mode,
            file_path=file_path,
            output_path=output_path,
            email=config_data.get('email'),
            membrane_config=membrane_config,
            input_protein_size_plus=config_data.get('input_protein_size_plus', 20),
            water_thickness_z=config_data.get('water_thickness_z', 22.5),
            ion_configuration=ion_configuration,
            temperature=config_data.get('temperature', 303.15),
            perform_charmm_minimization=config_data.get('perform_charmm_minimization', True),
            md_input_options=md_input_options
        )
    
    @staticmethod
    def save_to_yaml(request: PdbFileOptionRequest, yaml_path: Path) -> None:
        """
        Save a PdbFileOptionRequest object to a YAML file using human-readable enum names.
        
        Args:
            request: PdbFileOptionRequest object to save
            yaml_path: Path where to save the YAML file
        """
        config_dict = {
            'pdb_id': request.pdb_id,
            'file_input_mode': request.file_input_mode.name,
            'file_path': str(request.file_path) if request.file_path else None,
            'email': request.email,
            'membrane_config': {
                'membrane_type': request.membrane_config.membrane_type.name,
                'popc': request.membrane_config.popc,
                'dopc': request.membrane_config.dopc,
                'dspc': request.membrane_config.dspc,
                'dmpc': request.membrane_config.dmpc,
                'dppc': request.membrane_config.dppc,
                'chol_value': request.membrane_config.chol_value,
                'protein_topology': request.membrane_config.protein_topology.name
            },
            'input_protein_size_plus': request.input_protein_size_plus,
            'water_thickness_z': request.water_thickness_z,
            'ion_configuration': {
                'ion_concentration': request.ion_configuration.ion_concentration,
                'ion_type': request.ion_configuration.ion_type.name
            },
            'temperature': request.temperature,
            'perform_charmm_minimization': request.perform_charmm_minimization,
            'md_input_options': {
                'namd_enabled': request.md_input_options.namd_enabled,
                'gromacs_enabled': request.md_input_options.gromacs_enabled,
                'openmm_enabled': request.md_input_options.openmm_enabled
            }
        }
        
        with open(yaml_path, 'w') as file:
            yaml.dump(config_dict, file, default_flow_style=False, indent=2)


def load_yaml_config(yaml_path: str) -> PdbFileOptionRequest:
    """
    Convenience function to load a YAML configuration file.
    
    Args:
        yaml_path: Path to the YAML configuration file
        
    Returns:
        PdbFileOptionRequest object configured from YAML
    """
    return YamlConfigParser.parse_yaml_file(Path(yaml_path))