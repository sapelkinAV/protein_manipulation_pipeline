# OPRLM Biology Analysis Tool

A tool for automating biology analysis workflows, starting with PDB file loading from OPRLM.

## OPRLM Batch Downloader CLI

A command-line utility for batch processing PDB files through OPRLM using YAML configuration files.

### Quick Start

```bash
# Make the wrapper script executable
chmod +x oprlm-batch

# Run with example configurations
./oprlm-batch -i ./src/debug_scripts/examples -o ./data --user sapelkinav --config-pattern "*.yaml"

# Dry run to validate configurations
./oprlm-batch -i ./configs -o ./results --dry-run

# Process with custom settings
./oprlm-batch -i ./my_configs -o ./my_results --user alice --max-workers 2 --headless --continue-on-error
```

### CLI Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-i, --input-dir` | Directory with YAML configs | `./configs` |
| `-o, --output-dir` | Output directory for results | `./results` |
| `--user` | Username for launch ID | `alice` |
| `--config-pattern` | YAML file pattern | `"*.yaml"` |
| `--max-workers` | Concurrent jobs (default: 1) | `2` |
| `--headless` | Run browser headless | |
| `--continue-on-error` | Continue if individual jobs fail | |
| `--dry-run` | Validate configs without processing | |
| `-v, --verbose` | Enable verbose logging | |

### Output Structure

```
results/
├── alice_20250813_143052/
│   ├── 1ABC/
│   │   ├── processed.pdb
│   │   ├── md_input.tgz
│   │   ├── charmm-gui.tgz
│   │   └── metadata.json
│   ├── 2XYZ/
│   │   └── ...
│   ├── logs/
│   │   ├── batch.log
│   │   └── errors.log
│   └── summary.json
```

### YAML Configuration

Create YAML files to define processing parameters for each protein. See [YAML_CONFIGURATION.md](YAML_CONFIGURATION.md) for complete documentation.

**Quick example:**
```yaml
proteins:
  - pdb_id: "2RH1"
    file_input_mode: "searchPDB"
    membrane_type: "PMm"
    protein_topology: "in"
  - pdb_id: "custom_protein"
    file_input_mode: "upload"
    file_path: "/path/to/protein.pdb"
    membrane_type: "custom"
    popc: true
    chol_value: 25.0
```

### Alternative Usage (without wrapper)

```bash
PYTHONPATH=src python -m cli.oprlm_batch_downloader \
  -i ./configs -o ./results --user alice --config-pattern "*.yaml"
```

### Configuration Examples

The `src/debug_scripts/examples/` directory contains ready-to-use examples:

- `search_opm.yaml` - Search OPM database
- `search_rcsb.yaml` - Search RCSB PDB
- `custom_upload.yaml` - Process custom PDB files

Copy and modify these examples for your specific needs.
