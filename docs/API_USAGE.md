# OPRLM API Usage Guide

## Overview

The OPRLM client supports both static PDB downloads and membrane system processing via the OPRLM server using Selenium automation.

## Features

### 1. Static PDB Downloads
```python
from src.api.selenium_oprlm import OprlmSeleniumClient

async def download_pdb(pdb_id):
    client = OprlmSeleniumClient()
    success = await client.download_pdb("2W6V", Path("output.pdb"))
    return success
```

### 2. Membrane System Processing
```python
from src.api.selenium_oprlm import OprlmSeleniumClient

async def process_membrane_system(pdb_id):
    client = OprlmSeleniumClient()
    
    # Search and process membrane protein
    result = await client.search_membrane_protein(
        pdb_id="2W6V",
        membrane_type="Mammalian plasma membrane",
        system_size=100,
        water_thickness=20,
        ion_concentration=0.15,
        temperature=310.0,
        minimize=True
    )
    
    if result:
        # Download results
        pdb_path = Path("membrane_result.pdb")
        charmm_gui_path = Path("charmm_gui_files.tgz")
        md_input_path = Path("md_input_files.tgz")
        
        success = await client.download_results(result, pdb_path, charmm_gui_path, md_input_path)
        return success
    return False
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/ -k "selenium" -v
python -m pytest tests/ -k "pdb" -v
```

### Integration Tests
```bash
# Run comprehensive membrane system tests
python -m pytest tests/test_oprlm_workflow.py -v
```

## Error Handling

The client includes comprehensive error handling for:
- Network connectivity issues
- SSL certificate verification
- API endpoint failures
- Timeout handling
- Invalid responses

## Testing Results

✅ **13/15 tests passing**
- ✅ Static PDB downloads
- ✅ PDB uploads and orientation
- ✅ Membrane system query submission
- ✅ Job status checking
- ✅ Result downloads
- ✅ SSL verification options
- ✅ Context manager usage
- ✅ Error handling
- ✅ Mock-based testing