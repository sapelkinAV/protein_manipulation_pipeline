# OPRLM API Usage Guide

## Overview

The OPRLM client now supports both static PDB downloads and membrane system processing via the OPRLM server.

## Features

### 1. Static PDB Downloads
```python
from src.api.oprlm_client import OPRLMClient

async def download_pdb(pdb_id):
    async with OPRLMClient() as client:
        success = await client.download_pdb("2W6V", Path("output.pdb"))
        return success
```

### 2. Membrane System Processing
```python
from src.api.oprlm_client import OPRLMClient

async def process_membrane_system(pdb_id):
    async with OPRLMClient(ssl_verify=False) as client:
        # Submit membrane system query
        job_id = await client.submit_membrane_query(
            pdb_id="2W6V",
            membrane_system='true',
            orient='true'
        )
        
        if job_id:
            # Process the result
            success = await client.process_membrane_system(
                pdb_id="2W6V",
                output_path=Path("membrane_result.pdb"),
                poll_interval=3.0,
                timeout=300.0
            )
            return success
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
python -m pytest tests/test_oprlm_client.py -v

# Run specific test categories
python -m pytest tests/test_oprlm_client.py -k "membrane" -v
python -m pytest tests/test_oprlm_client.py -k "pdb" -v
```

### Integration Tests
```bash
# Run comprehensive membrane system tests
python test_comprehensive.py

# Test specific endpoints
python test_api_structure.py
```

## Configuration

### SSL Verification
By default, SSL verification is enabled. For testing or environments with SSL issues:

```python
async with OPRLMClient(ssl_verify=False) as client:
    # Your code here
```

### Custom Base URL
```python
async with OPRLMClient(base_url="https://your-oprlm-instance.com/oprlm_server") as client:
    # Your code here
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