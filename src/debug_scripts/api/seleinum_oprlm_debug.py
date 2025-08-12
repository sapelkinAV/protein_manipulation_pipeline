from pathlib import Path

from api.models import MembraneConfig, MembraneType, ProteinTopologyMembrane, PdbFileOptionRequest, \
    ProteinStructure, IonConfiguration, IonType, MDInputOptions
from api.selenium_oprlm import OprlmSeleniumClient


def download_selenium_oprlm_from_file():
    # Example for CUSTOM upload - using the test PDB file
    test_pdb_path = Path(__file__).parent.parent / "2W6V.pdb"

    if not test_pdb_path.exists():
        print(f"Test PDB file not found: {test_pdb_path}")
        print("Please ensure tests/2W6V.pdb exists")
        exit(1)

    print(f"Using test PDB file: {test_pdb_path}")
    membrane_config = MembraneConfig.builder() \
        .membrane_type(MembraneType.CUSTOM) \
        .popc(True) \
        .dopc(True) \
        .dspc(True) \
        .dmpc(True) \
        .dppc(True) \
        .chol_value(30.0) \
        .protein_topology(topology=ProteinTopologyMembrane.OUT) \
        .build()

    file_request = PdbFileOptionRequest.builder() \
        .pdb_id("2W6V_custom") \
        .file_input_mode(ProteinStructure.CUSTOM) \
        .file_path(test_pdb_path) \
        .membrane_config(membrane_config) \
        .email("abobus@gmail.com") \
        .input_protein_size_plus(20) \
        .water_thickness_z(25.0) \
        .ion_configuration(IonConfiguration.builder()
                           .ion_concentration(0.15)
                           .ion_type(IonType.NaCl)
                           .build()) \
        .temperature(310.0) \
        .perform_charmm_minimization(False) \
        .md_input_options(MDInputOptions.builder()
                          .namd_enabled(True)
                          .gromacs_enabled(False)
                          .openmm_enabled(False)
                          .build()) \
        .build()

    download_pdb(file_request)

def download_pdb_via_search_mode():
    membrane_config = MembraneConfig.builder() \
        .membrane_type(MembraneType.CUSTOM) \
        .popc(True) \
        .dopc(True) \
        .dspc(True) \
        .dmpc(True) \
        .dppc(True) \
        .chol_value(30.0) \
        .protein_topology(topology=ProteinTopologyMembrane.OUT) \
        .build()

    file_request = PdbFileOptionRequest.builder() \
        .pdb_id("3c02") \
        .file_input_mode(ProteinStructure.OPRLM) \
        .output_path("/Users/sapelkinav/code/python/oprlm/data/results/3c02") \
        .membrane_config(membrane_config) \
        .email("abobus@gmail.com") \
        .input_protein_size_plus(20) \
        .water_thickness_z(25.0) \
        .ion_configuration(IonConfiguration.builder()
                           .ion_concentration(0.15)
                           .ion_type(IonType.NaCl)
                           .build()) \
        .temperature(310.0) \
        .perform_charmm_minimization(False) \
        .md_input_options(MDInputOptions.builder()
                          .namd_enabled(True)
                          .gromacs_enabled(False)
                          .openmm_enabled(False)
                          .build()) \
        .build()
    download_pdb(file_request)


def download_pdb(file_request):
    try:
        oprlm_client = OprlmSeleniumClient(headless=False)
        oprlm_client.get_oprlm_processed_pdb(pdb_file_request=file_request)
    except Exception as e:
        print(f"Error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Chrome is installed")
        print("2. Try running with headless=True")
        print("3. Check internet connection")
        print("4. Use the example script: python examples/custom_upload_example.py")
    finally:
        if 'oprlm_client' in locals() and oprlm_client.driver:
            oprlm_client.driver.quit()

if __name__ == "__main__":
    download_pdb_via_search_mode()