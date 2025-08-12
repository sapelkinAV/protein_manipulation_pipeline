"""
Debug script for OPRLM selenium client using YAML configuration.

This script provides the same functionality as seleinum_oprlm_debug.py
but reads the configuration from YAML files instead of hardcoded values.
"""

import sys
import argparse
from pathlib import Path

from api.models import PdbFileOptionRequest
from api.selenium_oprlm import OprlmSeleniumClient
from utils.yaml_parser import load_yaml_config

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))




def download_selenium_oprlm_from_yaml(yaml_config_path: str):
    """
    Download processed PDB from OPRLM using YAML configuration.
    
    Args:
        yaml_config_path: Path to the YAML configuration file
    """
    try:
        # Parse YAML configuration
        print(f"Loading configuration from: {yaml_config_path}")
        file_request = load_yaml_config(yaml_config_path)
        
        # Validate file path for CUSTOM mode
        if file_request.file_input_mode.value == "upload" and file_request.file_path:
            if not file_request.file_path.exists():
                print(f"PDB file not found: {file_request.file_path}")
                print("Please ensure the file exists at the specified path")
                return
            print(f"Using PDB file: {file_request.file_path}")
        
        print(f"Configuration loaded successfully:")
        print(f"  PDB ID: {file_request.pdb_id}")
        print(f"  Mode: {file_request.file_input_mode.value}")
        print(f"  Membrane type: {file_request.membrane_config.membrane_type.value}")
        
        # Process the request
        download_pdb(file_request)
        
    except Exception as e:
        print(f"Error loading YAML configuration: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure the YAML file exists and is properly formatted")
        print("2. Check that all required fields are present")
        print("3. Verify file paths are correct")


def download_pdb(file_request: PdbFileOptionRequest):
    """Download processed PDB using the selenium client."""
    try:
        oprlm_client = OprlmSeleniumClient(headless=False)
        oprlm_client.get_oprlm_processed_pdb(pdb_file_request=file_request)
        print("Download completed successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Chrome is installed")
        print("2. Try running with headless=True")
        print("3. Check internet connection")
        print("4. Verify OPRLM server is accessible")
    finally:
        if 'oprlm_client' in locals() and oprlm_client.driver:
            oprlm_client.driver.quit()

def load_CUSTOM() -> PdbFileOptionRequest:
    return load_yaml_config("/Users/sapelkinav/code/python/oprlm/src/debug_scripts/examples/custom_upload.yaml")

def load_OPM() -> PdbFileOptionRequest:
    return load_yaml_config("/Users/sapelkinav/code/python/oprlm/src/debug_scripts/examples/search_opm.yaml")

def load_RCSB() -> PdbFileOptionRequest:
    return load_yaml_config("/Users/sapelkinav/code/python/oprlm/src/debug_scripts/examples/search_rcsb.yaml")

if __name__ == "__main__":
    download_pdb(load_OPM())
