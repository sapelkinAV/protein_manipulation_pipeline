# OPRLM Biology Analysis Tool

A tool for automating biology analysis workflows, starting with PDB file loading from OPRLM.

## Features

- **PDB File Management**: Download from OPRLM or upload local PDB files
- **Analysis Planning**: Create and manage multi-step analysis plans
- **Terminal GUI**: Rich terminal interface for managing plans and executions
- **Extensible Architecture**: Pluggable step system for adding new analysis stages

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Terminal GUI
Launch the terminal interface:
```bash
python main.py --gui
```

### Command Line
Create a sample plan:
```bash
python main.py --create-sample
```

List existing plans:
```bash
python main.py --list
```

## Architecture

### Core Components

- **Plan Manager** (`src/core/plan_manager.py`): Manages analysis plans and their state
- **OPRLM Client** (`src/api/oprlm_client.py`): Handles communication with OPRLM server
- **Steps** (`src/steps/`): Individual analysis step implementations
- **GUI** (`src/gui/`): Terminal-based user interface

### Directory Structure

```
oprlm/
├── src/
│   ├── api/           # API clients
│   ├── core/          # Core models and management
│   ├── gui/           # Terminal GUI
│   ├── steps/         # Analysis step implementations
│   └── utils/         # Utility functions
├── tests/             # Test files
├── plans/             # Stored analysis plans (JSON)
├── data/              # Downloaded PDB files
├── results/           # Analysis results
└── config/            # Configuration files
```

## Usage Examples

### Creating a Plan
```python
from src.core.plan_manager import PlanManager

plan_manager = PlanManager()
plan = plan_manager.create_plan(
    name="My Analysis",
    description="Analysis of protein 1ABC",
    pdb_id="1ABC"
)

# Add a PDB fetch step
from src.core.models import AnalysisStep
fetch_step = AnalysisStep(
    name="fetch_pdb",
    description="Download PDB file",
    step_type="pdb_fetch",
    parameters={"pdb_id": "1ABC"}
)
plan_manager.add_step(plan.id, fetch_step)
```

### Running Analysis
```python
from src.steps.pdb_fetch import PDBFetchStep

step = AnalysisStep(
    name="fetch_pdb",
    description="Download PDB file",
    step_type="pdb_fetch",
    parameters={"pdb_id": "1ABC", "output_filename": "1abc.pdb"}
)

fetch_step = PDBFetchStep(step, Path("./working_dir"))
result = await fetch_step.execute()
```

## Development

### Adding New Steps

1. Create a new step class in `src/steps/`
2. Inherit from `BaseStep`
3. Implement the `execute` method
4. Add step type to the GUI

Example:
```python
from src.steps.base import BaseStep

class MyAnalysisStep(BaseStep):
    async def execute(self) -> Dict[str, Any]:
        # Your analysis logic here
        return {"result": "success"}
```

### API Endpoints

The tool currently supports:
- **PDB Download**: `https://oprlm.org/static/{pdb_id}.pdb`
- **PDB Orient**: `https://oprlm.org/oprlm_server/orient`
- **Job Status**: `https://oprlm.org/oprlm_server/job/{job_id}`

## Future Steps

1. **CAVER Integration**: Run CAVER analysis on PDB files
2. **Z-slice Grid Generation**: Create search grids for pore analysis
3. **Fragment Library Screening**: Implement FASTDock-style scoring
4. **Full Ligand Docking**: Redock/minimize ligands at fragment seeds

## License

[Add your license here]