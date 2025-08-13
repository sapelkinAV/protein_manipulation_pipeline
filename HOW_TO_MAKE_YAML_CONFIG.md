# YAML Configuration Guide for OPRLM Batch Processing

This document provides comprehensive guidance for creating YAML configuration files compatible with the OPRLM batch processing system.

## Overview

YAML configuration files define the parameters for processing individual protein structures through the OPRLM web service. Each YAML file configures a single protein processing job.

## File Structure

A YAML configuration file contains parameters for a single protein processing job:

```yaml
pdb_id: "1ABC"
file_input_mode: RCSB
# ... other parameters
```

## Required Parameters

### `pdb_id` (string)
- **Description**: Unique identifier for the protein
- **Usage**: 
  - For RCSB search: Use the actual PDB ID (e.g., "1A1U", "2RH1")
  - For OPM search: Use the OPM identifier (e.g., "3c02")
  - For custom upload: Use any descriptive name (e.g., "2W6V_custom")

### `file_input_mode` (string)
- **Description**: Source of the protein structure
- **Valid values**:
  - `RCSB` - Search RCSB Protein Data Bank
  - `OPRLM` - Search OPM (Orientations of Proteins in Membranes)
  - `CUSTOM` - Upload custom PDB file

## Optional Parameters

### File Handling

#### `file_path` (string)
- **Description**: Path to custom PDB file (required when `file_input_mode` is `CUSTOM`)
- **Example**: `/Users/username/proteins/my_protein.pdb`

#### `output_path` (string)
- **Description**: Custom output directory for results
- **Default**: Auto-generated directory with timestamp
- **Example**: `data/results/1A1U`

#### `email` (string)
- **Description**: Email address for notifications
- **Example**: `user@institution.edu`

### Membrane Configuration

#### `membrane_type` (string)
- **Description**: Type of membrane to embed the protein in
- **Default**: `CUSTOM`
- **Valid values**:
  - `CUSTOM` - Simple model membrane
  - `PM_MAMMALIAN` - Plasma membrane (mammalian)
  - `PM_PLANTS` - Plasma membrane (plants)
  - `PM_FUNGI` - Plasma membrane (fungi)
  - `ER_FUNGI` - ER (fungi)
  - `ER_MAMMALIAN` - ER (mammalian)
  - `GOLGI_MAMMALIAN` - Golgi membrane (mammalian)
  - `GOLGI_FUNGI` - Golgi membrane (fungi)
  - `ENDOSOME_MAMMALIAN` - Endosome membrane (mammalian)
  - `LYSOSOME_MAMMALIAN` - Lysosome membrane (mammalian)
  - `OUTER_MITOCHONDRIAL` - Outer mitochondrial membrane
  - `INNER_MITOCHONDRIAL` - Inner mitochondrial membrane
  - `VACUOLE` - Vacuole membrane (plants)
  - `THYLAKOID_PLANTS` - Thylakoid membrane (plants)
  - `THYLAKOID_CYANOBACTERIA` - Thylakoid membrane (cyanobacteria)
  - `BACT_OUTER` - Outer membrane (Gram-negative bacteria)
  - `BACT_INNER` - Inner membrane (Gram-negative bacteria)
  - `BACT_POSITIVE` - Plasma membrane (Gram-positive bacteria)
  - `ARCHAEA` - Archaeal plasma membrane
  - `GRAM_NEGATIVE_BACTERIA_OUTER_MEMBRANE` - Gram-negative bacteria outer membrane
  - `GRAM_NEGATIVE_BACTERIA_INNER_MEMBRANE` - Gram-negative bacteria inner membrane
  - `GRAM_POSITIVE_BACTERIA_MEMBRANE` - Gram-positive bacteria membrane

#### `protein_topology` (string)
- **Description**: Protein orientation relative to membrane
- **Default**: `IN`
- **Valid values**: `IN`, `OUT`

#### Lipid Composition (for CUSTOM membranes)
- **Description**: Boolean flags for lipid types in custom membranes
- **Valid values**: `true` or `false`
- **Available lipids**:
  - `popc` (default: `true`) - Palmitoyloleoylphosphatidylcholine
  - `dopc` (default: `false`) - Dioleoylphosphatidylcholine
  - `dspc` (default: `false`) - Distearoylphosphatidylcholine
  - `dmpc` (default: `false`) - Dimyristoylphosphatidylcholine
  - `dppc` (default: `false`) - Dipalmitoylphosphatidylcholine

#### `chol_value` (float)
- **Description**: Cholesterol concentration percentage (0-100)
- **Default**: `20.0`
- **Example**: `30.0` for 30% cholesterol

### Ion Configuration

#### `ion_concentration` (float)
- **Description**: Ion concentration in molar units
- **Default**: `0.15` (150 mM)
- **Example**: `0.1` for 100 mM, `0.7` for 700 mM

#### `ion_type` (string)
- **Description**: Type of salt for the solution
- **Default**: `KCl`
- **Valid values**: `KCl`, `NaCl`, `CaCl2`, `MgCl2`

### Simulation Parameters

#### `temperature` (float)
- **Description**: Simulation temperature in Kelvin
- **Note**: Examples use Celsius values (298.0 = 25°C, 310.0 = 37°C)
- **Example**: `298.0`, `310.0`

#### `water_thickness_z` (float)
- **Description**: Water layer thickness in Angstroms
- **Default**: `22.5`
- **Example**: `20.0`, `25.0`

#### `input_protein_size_plus` (int)
- **Description**: Additional padding around protein in Angstroms
- **Default**: `20`
- **Example**: `15`, `20`, `25`

#### `perform_charmm_minimization` (boolean)
- **Description**: Whether to perform CHARMM energy minimization
- **Default**: `true`
- **Valid values**: `true`, `false`

### MD Input Options

#### `namd_enabled` (boolean)
- **Description**: Generate NAMD input files
- **Default**: `false`
- **Valid values**: `true`, `false`

#### `gromacs_enabled` (boolean)
- **Description**: Generate GROMACS input files
- **Default**: `true`
- **Valid values**: `true`, `false`

#### `openmm_enabled` (boolean)
- **Description**: Generate OpenMM input files
- **Default**: `true`
- **Valid values**: `true`, `false`

## Complete Example Configurations

### Example 1: OPM Search with Custom Membrane (from search_opm.yaml)
```yaml
pdb_id: "3c02"
file_input_mode: OPRLM
output_path: "data/results/3c02"
email: "abobus@gmail.com"

membrane_config:
  membrane_type: CUSTOM
  popc: true
  dopc: true
  dspc: true
  dmpc: true
  dppc: true
  chol_value: 80.0
  protein_topology: OUT

input_protein_size_plus: 20
water_thickness_z: 25.0

ion_configuration:
  ion_concentration: 0.70
  ion_type: NaCl

temperature: 25.0
perform_charmm_minimization: false

md_input_options:
  namd_enabled: true
  gromacs_enabled: false
  openmm_enabled: true
```

### Example 2: RCSB Search with Mammalian Membrane (from search_rcsb.yaml)
```yaml
pdb_id: "1A1U"
file_input_mode: RCSB
output_path: "data/results/1A1U"
email: "abobus@gmail.com"

membrane_config:
  membrane_type: PM_MAMMALIAN
  protein_topology: IN

input_protein_size_plus: 15
water_thickness_z: 20.0

ion_configuration:
  ion_concentration: 0.1
  ion_type: KCl

temperature: 298.0
perform_charmm_minimization: true

md_input_options:
  namd_enabled: false
  gromacs_enabled: true
  openmm_enabled: true
```

### Example 3: Custom Upload with Custom Membrane (from custom_upload.yaml)
```yaml
pdb_id: "2W6V_custom"
file_input_mode: CUSTOM
file_path: "/Users/username/proteins/2W6V.pdb"
email: "abobus@gmail.com"

membrane_config:
  membrane_type: CUSTOM
  popc: true
  dopc: true
  dspc: true
  dmpc: true
  dppc: true
  chol_value: 30.0
  protein_topology: OUT

input_protein_size_plus: 20
water_thickness_z: 25.0

ion_configuration:
  ion_concentration: 0.15
  ion_type: NaCl

temperature: 310.0
perform_charmm_minimization: false

md_input_options:
  namd_enabled: true
  gromacs_enabled: false
  openmm_enabled: false
```

## Validation Rules

1. **Required fields**: Each protein entry must have `pdb_id` and `file_input_mode`
2. **File existence**: When `file_input_mode` is `"upload"`, the `file_path` must exist
3. **Value ranges**:
   - `chol_value`: 0.0 to 100.0
   - `ion_concentration`: 0.0 to 2.0 (reasonable biological range)
   - `temperature`: 270.0 to 400.0 (Kelvin)
   - `water_thickness_z`: 10.0 to 50.0 (Angstroms)
4. **String values**: Must match exactly with the valid values listed above

## Tips for Creating YAML Files

1. **Use consistent indentation**: Use 2 spaces for indentation (not tabs)
2. **Quote strings**: Use quotes for string values, especially those containing special characters
3. **Test your YAML**: Use online YAML validators to check syntax
4. **Start simple**: Begin with minimal required parameters and add complexity gradually
5. **Use examples**: Copy and modify the provided examples rather than starting from scratch

## Common Mistakes to Avoid

1. **Incorrect enum values**: Ensure `file_input_mode`, `membrane_type`, etc. use exact valid strings
2. **Missing required fields**: Always include `pdb_id` and `file_input_mode`
3. **Wrong data types**: Use strings for text, numbers for numeric values, and booleans for flags
4. **Invalid file paths**: Ensure file paths exist when using `"upload"` mode
5. **Inconsistent formatting**: Maintain consistent indentation throughout the file

## Testing Your Configuration

Before running batch processing, test your YAML configuration:

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('your_config.yaml'))"

# Test with dry-run mode
python src/cli/oprlm_batch_downloader.py --config your_config.yaml --dry-run

# Check available examples
python src/debug_scripts/api/seleinum_oprlm_debug_yaml.py --list-examples
```