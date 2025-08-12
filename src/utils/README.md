# YAML Configuration Parser for OPRLM

This directory contains utilities for parsing YAML configuration files into `PdbFileOptionRequest` objects for use with the OPRLM selenium client.

## Files

- `yaml_parser.py`: Main YAML parser utility
- `README.md`: This documentation file

## Usage

### Loading from YAML file

```python
from src.utils.yaml_parser import load_yaml_config

# Load configuration from YAML file
config = load_yaml_config("path/to/config.yaml")

# Use with OPRLM client
from src.api.selenium_oprlm import OprlmSeleniumClient

client = OprlmSeleniumClient()
client.get_oprlm_processed_pdb(pdb_file_request=config)
```

### YAML Configuration Format

The YAML configuration supports all fields of `PdbFileOptionRequest`:

```yaml
# Required fields
pdb_id: "your_pdb_id"
file_input_mode: "upload"  # or "searchPDB", "searchOPM"

# Optional fields
file_path: "path/to/pdb/file.pdb"  # Required for "upload" mode
output_path: "path/to/output/directory"
email: "your@email.com"

# Membrane configuration
membrane_config:
  membrane_type: "custom"  # See MembraneType enum for options
  popc: true
  dopc: false
  dspc: false
  dmpc: false
  dppc: false
  chol_value: 20.0
  protein_topology: "in"  # or "out"

# System parameters
input_protein_size_plus: 20
water_thickness_z: 22.5
temperature: 303.15
perform_charmm_minimization: true

# Ion configuration
ion_configuration:
  ion_concentration: 0.15
  ion_type: "NaCl"  # or "KCl", "CaCl2", "MgCl2"

# MD input options
md_input_options:
  namd_enabled: false
  gromacs_enabled: true
  openmm_enabled: true
```

### Creating Example Configurations

Use the debug script to create example configurations:

```bash
python src/debug_scripts/api/seleinum_oprlm_debug_yaml.py --create-examples
```

This will create example YAML files in `src/debug_scripts/examples/`.

### Available Example Configurations

- `custom_upload.yaml`: Upload custom PDB file
- `search_opm.yaml`: Search OPRLM database
- `search_rcsb.yaml`: Search RCSB PDB database

## API Reference

### `YamlConfigParser`

Main class for parsing YAML configurations.

#### Methods

- `parse_yaml_file(yaml_path: Path) -> PdbFileOptionRequest`: Parse YAML file
- `parse_yaml_string(yaml_string: str) -> PdbFileOptionRequest`: Parse YAML string
- `parse_dict(config_data: Dict[str, Any]) -> PdbFileOptionRequest`: Parse dictionary
- `save_to_yaml(request: PdbFileOptionRequest, yaml_path: Path) -> None`: Save request to YAML

### `load_yaml_config(yaml_path: str) -> PdbFileOptionRequest`

Convenience function to load configuration from YAML file.
