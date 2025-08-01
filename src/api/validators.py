from src.api.models import MembraneConfig, ProteinStructure, MembraneType, ProteinTopologyMembrane, IonConfiguration, IonType


class MembraneConfigValidator:
    """Validation utilities for MembraneConfig"""

    @staticmethod
    def validate_membrane_config(membrane_config: MembraneConfig):
        """Comprehensive validation for MembraneConfig to prevent None values"""
        if membrane_config is None:
            raise ValueError("membrane_config cannot be None")
        
        # Validate membrane_type
        if membrane_config.membrane_type is None:
            raise ValueError("membrane_type cannot be None")
        if not isinstance(membrane_config.membrane_type, MembraneType):
            raise TypeError(f"membrane_type must be a MembraneType enum, got {type(membrane_config.membrane_type)}")
        
        # Validate protein_topology
        if membrane_config.protein_topology is None:
            raise ValueError("protein_topology cannot be None")
        if not isinstance(membrane_config.protein_topology, ProteinTopologyMembrane):
            raise TypeError(f"protein_topology must be a ProteinTopologyMembrane enum, got {type(membrane_config.protein_topology)}")
        
        # Validate cholesterol value
        if membrane_config.chol_value is None:
            raise ValueError("chol_value cannot be None")
        if not isinstance(membrane_config.chol_value, (int, float)):
            raise TypeError(f"chol_value must be a number, got {type(membrane_config.chol_value)}")
        if not (0 <= membrane_config.chol_value <= 100):
            raise ValueError(f"chol_value must be between 0 and 100, got {membrane_config.chol_value}")
        
        # Validate boolean lipid fields
        bool_fields = ['popc', 'dopc', 'dspc', 'dmpc', 'dppc']
        for field_name in bool_fields:
            value = getattr(membrane_config, field_name, None)
            if value is None:
                raise ValueError(f"{field_name} cannot be None")
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean value, got {type(value)}")

    @staticmethod
    def validate_inputs(protein_structure: ProteinStructure, membrane_config: MembraneConfig):
        """Validate both protein_structure and membrane_config inputs"""
        if protein_structure is None:
            raise ValueError("protein_structure cannot be None")
        if not isinstance(protein_structure, ProteinStructure):
            raise TypeError(f"protein_structure must be a ProteinStructure enum, got {type(protein_structure)}")
        
        MembraneConfigValidator.validate_membrane_config(membrane_config)

    @staticmethod
    def sanitize_chol_value(value):
        """Sanitize cholesterol value to ensure it's within valid range"""
        if value is None:
            return 0.0
        try:
            float_value = float(value)
            return max(0.0, min(100.0, float_value))
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def sanitize_boolean(value, default=False):
        """Sanitize boolean values"""
        if value is None:
            return default
        return bool(value)


class PdbFileOptionRequestValidator:
    """Validation utilities for PdbFileOptionRequest"""

    @staticmethod
    def validate_pdb_file_request(request):
        """Validate PdbFileOptionRequest"""
        if request is None:
            raise ValueError("PdbFileOptionRequest cannot be None")
        
        if request.pdb_id is None or not isinstance(request.pdb_id, str):
            raise ValueError("pdb_id must be a non-empty string")
        if not request.pdb_id.strip():
            raise ValueError("pdb_id cannot be empty")
        
        if request.file_input_mode is None:
            raise ValueError("file_input_mode cannot be None")
        if not isinstance(request.file_input_mode, ProteinStructure):
            raise TypeError(f"file_input_mode must be a ProteinStructure enum, got {type(request.file_input_mode)}")
        
        if request.membrane_config is not None:
            MembraneConfigValidator.validate_membrane_config(request.membrane_config)
        
        if request.input_protein_size_plus is None:
            raise ValueError("input_protein_size_plus cannot be None")
        if not isinstance(request.input_protein_size_plus, int):
            raise TypeError(f"input_protein_size_plus must be an integer, got {type(request.input_protein_size_plus)}")
        if not (1 <= request.input_protein_size_plus <= 100):
            raise ValueError(f"input_protein_size_plus must be between 1 and 100, got {request.input_protein_size_plus}")
        
        if request.water_thickness_z is None:
            raise ValueError("water_thickness_z cannot be None")
        if not isinstance(request.water_thickness_z, (int, float)):
            raise TypeError(f"water_thickness_z must be a number, got {type(request.water_thickness_z)}")
        if not (1.0 <= request.water_thickness_z <= 100.0):
            raise ValueError(f"water_thickness_z must be between 1.0 and 100.0, got {request.water_thickness_z}")
        
        if request.ion_configuration is None:
            raise ValueError("ion_configuration cannot be None")
        if not isinstance(request.ion_configuration, IonConfiguration):
            raise TypeError(f"ion_configuration must be an IonConfiguration, got {type(request.ion_configuration)}")
        
        # Validate ion concentration
        if request.ion_configuration.ion_concentration is None:
            raise ValueError("ion_concentration cannot be None")
        if not isinstance(request.ion_configuration.ion_concentration, (int, float)):
            raise TypeError(f"ion_concentration must be a number, got {type(request.ion_configuration.ion_concentration)}")
        if not (0.0 <= request.ion_configuration.ion_concentration <= 5.0):
            raise ValueError(f"ion_concentration must be between 0.0 and 5.0, got {request.ion_configuration.ion_concentration}")
        
        # Validate ion type
        if request.ion_configuration.ion_type is None:
            raise ValueError("ion_type cannot be None")
        if not isinstance(request.ion_configuration.ion_type, IonType):
            raise TypeError(f"ion_type must be an IonType enum, got {type(request.ion_configuration.ion_type)}")
        
        # Validate temperature
        if request.temperature is None:
            raise ValueError("temperature cannot be None")
        if not isinstance(request.temperature, (int, float)):
            raise TypeError(f"temperature must be a number, got {type(request.temperature)}")
        if not (100.0 <= request.temperature <= 400.0):
            raise ValueError(f"temperature must be between 100.0 and 400.0 K, got {request.temperature}")