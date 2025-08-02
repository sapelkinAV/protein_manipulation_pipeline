from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.api.models import ProteinStructure, MembraneConfig, MembraneType, ProteinTopologyMembrane, PdbFileOptionRequest, IonConfiguration, IonType, MDInputOptions
from src.api.validators import MembraneConfigValidator

PROTEIN_STRUCTURE_FIELD_NAME = "fileInputMode"
MEMBRANE_TYPE_FIELD_NAME = "membraneType"

class OprlmSeleniumClient:

    def __init__(self):
        self.driver = None

    def init_selenium_oprlm_session(self, headless=True):
        chrome_options = self.get_default_chrome_options()
        if headless:
            chrome_options.add_argument("--headless")

        try:
            # Use ChromeDriverManager to automatically manage the ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"ChromeDriver initialization failed: {e}")
            print("Trying alternative ChromeDriver setup...")
            
            # Try alternative setup
            try:
                from selenium.webdriver.chrome.service import Service as ChromeService
                service = ChromeService()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                print(f"Alternative setup also failed: {e2}")
                raise
        
        self.driver.get("https://oprlm.org/oprlm_server")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )


    def search_membrane_protein(self, pdb_file_request: PdbFileOptionRequest):
        # Select the file input mode
        self.__select_protein_structure(pdb_file_request.file_input_mode)

        if pdb_file_request.file_input_mode == ProteinStructure.RCSB or pdb_file_request.file_input_mode == ProteinStructure.OPRLM:
            self.__fill_search_field("search-box", pdb_file_request.pdb_id)
            # Click the search button specifically within the api-search div
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.api-search span.submit-button"))
            )
            search_button.click()
            
            # Wait for search results to load
            # Use universal indicators like chain table or NGL viewer
            WebDriverWait(self.driver, 30).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "chain-table")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".membrane-wide canvas")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'NGL Viewer')]"))
                )
            )
            
            # Check for error messages
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'PDB entry was not found') or contains(text(), 'not found')]")
            if error_elements:
                error_text = error_elements[0].text
                raise Exception(f"Search failed: {error_text}")
            
            print(f"✅ Search completed successfully for {pdb_file_request.pdb_id}")
            # Wait for chains to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#chain-table input[type='checkbox']"))
            )
            
        elif pdb_file_request.file_input_mode == ProteinStructure.CUSTOM:
            if not pdb_file_request.file_path:
                raise ValueError("file_path is required for CUSTOM file input mode")
            self.__upload_custom_pdb_file(pdb_file_request.file_path)

    def submit_job(self, pdb_file_request: PdbFileOptionRequest):

        # Fill membrane configuration based on MembraneConfig

        # Fill composition checkboxes
        self.__fill_membrane_config(pdb_file_request.file_input_mode, pdb_file_request.membrane_config)

        # Fill input_protein_size_plus (Box Margin Å)
        self.__fill_text_field(By.NAME, "nlayer", str(pdb_file_request.input_protein_size_plus))
        
        # Fill water_thickness_z (Water thickness along Z)
        self.__fill_text_field(By.NAME, "wdist", str(pdb_file_request.water_thickness_z))
        
        # Fill ion concentration and type
        self.__fill_text_field(By.NAME, "ion_conc", str(pdb_file_request.ion_configuration.ion_concentration))
        self.__select_dropdown_value("ion_type", pdb_file_request.ion_configuration.ion_type.value)
        
        # Fill temperature
        self.__fill_text_field(By.NAME, "temperature", str(pdb_file_request.temperature))
        
        # Fill minimization (select True/False for CHARMM minimization)
        minimization_value = "1" if pdb_file_request.perform_charmm_minimization else "0"
        self.__select_dropdown_value("charmm_mini", minimization_value)

        # Fill MD input options (NAMD, GROMACS, OpenMM checkboxes)
        self.__set_checkbox_value("namd_checked", pdb_file_request.md_input_options.namd_enabled)
        self.__set_checkbox_value("gmx_checked", pdb_file_request.md_input_options.gromacs_enabled)
        self.__set_checkbox_value("omm_checked", pdb_file_request.md_input_options.openmm_enabled)

        # Fill email and submit job
        self.__fill_text_field(By.ID, "userEmail", pdb_file_request.email or "abobus@gmail.com")
        
        submit_button = self.driver.find_element(By.ID, "submit")
        submit_button.click()
        
        print("Job submitted, waiting for completion...")
        
        # Wait for job completion and download links
        WebDriverWait(self.driver, 3600).until(
            EC.presence_of_element_located((By.ID, "download_pdb"))
        )
        
        print("Job completed! Downloading files...")

        # Use output_dir from PdbFileOptionRequest or create default
        download_dir = pdb_file_request.output_dir
        download_dir.mkdir(parents=True, exist_ok=True)
        # Download all files
        self.download_results(download_dir)
        
    def download_results(self, download_directory: Path):
        import requests
        
        # Get all download links
        pdb_link = self.driver.find_element(By.ID, "download_pdb").get_attribute("href")
        ess_link = self.driver.find_element(By.ID, "download_ess").get_attribute("href")
        tgz_link = self.driver.find_element(By.ID, "download_tgz").get_attribute("href")
        
        # Download files with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Referer': 'https://oprlm.org/'
        }
        
        files_to_download = [
            (pdb_link, "step5_assembly.pdb"),
            (ess_link, "md_input.tgz"),
            (tgz_link, "charmm-gui.tgz")
        ]
        
        for url, filename in files_to_download:
            if url:
                filepath = download_directory / filename
                print(f"Downloading {filename}...")
                
                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Downloaded {filename} to {filepath}")
            else:
                print(f"Warning: {filename} link not found")


    def get_default_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        return options

    def __select_protein_structure(self, prot_structure: ProteinStructure):
        self.__select_dropdown_value(PROTEIN_STRUCTURE_FIELD_NAME, prot_structure.value)

    def __fill_membrane_config(self, protein_structure: ProteinStructure, membrane_config: MembraneConfig):
        # Validate inputs using centralized validator
        MembraneConfigValidator.validate_inputs(protein_structure, membrane_config)
        
        # Select membrane type
        self.__select_dropdown_value(MEMBRANE_TYPE_FIELD_NAME, membrane_config.membrane_type.value)

        # FOR OPRLM AND RCSB Simple membrane type
        if (protein_structure in [ProteinStructure.OPRLM, ProteinStructure.RCSB] and 
                membrane_config.membrane_type == MembraneType.CUSTOM):
            self.__set_checkbox_value("popc", membrane_config.popc)
            self.__set_checkbox_value("dopc", membrane_config.dopc)
            self.__set_checkbox_value("dspc", membrane_config.dspc)
            self.__set_checkbox_value("dmpc", membrane_config.dmpc)
            self.__set_checkbox_value("dppc", membrane_config.dppc)

            self.__fill_text_field(By.NAME, "customChol", str(membrane_config.chol_value))

        # Fill Protein Topology in Membrane
        if protein_structure in [ProteinStructure.CUSTOM, ProteinStructure.RCSB]:
            self.__set_protein_topology_radio_button(membrane_config.protein_topology)



    def __set_protein_topology_radio_button(self, protein_topology: ProteinTopologyMembrane):
        radio_button = self.driver.find_element(By.ID, f"ppm_topology_{protein_topology.value}")
        radio_button.click()

    def __set_checkbox_value(self, checkbox_name: str, should_check: bool = True):
        checkbox = self.driver.find_element(By.NAME, checkbox_name)
        is_checked = checkbox.is_selected()

        if should_check and not is_checked:
            checkbox.click()
        elif not should_check and is_checked:
            checkbox.click()

    def __select_dropdown_value(self, dropdown_name: str, dropdown_value: str):
        dropdown_element = self.driver.find_element(By.NAME, dropdown_name)
        dropdown = Select(dropdown_element)
        dropdown.select_by_value(dropdown_value)

    def __fill_text_field(self, by, selector: str, text: str):
        """Utility method to fill text fields with clear and send_keys"""
        element = self.driver.find_element(by, selector)
        element.clear()
        element.send_keys(str(text))

    def __fill_search_field(self, selector: str, search_text: str):
        """Specialized for search fields"""
        self.__fill_text_field(By.ID, selector, search_text)

    def __upload_custom_pdb_file(self, pdb_file_path):
        """Upload a custom PDB file to OPRLM server"""
        # Convert to Path object if it's a string
        if isinstance(pdb_file_path, str):
            pdb_file_path = Path(pdb_file_path)
        elif not isinstance(pdb_file_path, Path):
            raise TypeError(f"pdb_file_path must be a string or Path object, got {type(pdb_file_path)}")
            
        if not pdb_file_path.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_file_path}")
        
        if not pdb_file_path.suffix.lower() in ['.pdb', '.cif']:
            raise ValueError(f"Unsupported file format: {pdb_file_path.suffix}. Only .pdb and .cif files are supported.")
        
        print(f"Uploading file: {pdb_file_path.absolute()}")
        
        # Find the file upload input element - wait for it to be visible and enabled
        file_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='pdbFile'][type='file']"))
        )
        
        # Ensure the file input is visible and enabled
        WebDriverWait(self.driver, 10).until(
            lambda driver: file_input.is_displayed() and file_input.is_enabled()
        )
        
        # Upload the file using absolute path
        absolute_path = str(pdb_file_path.absolute())
        file_input.send_keys(absolute_path)
        
        # Wait for file to be processed (button becomes enabled)
        # Use explicit wait instead of sleep
        upload_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Upload PDB File' and not(contains(@class, 'disabled'))]"))
        )
        
        # Scroll to the button and click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", upload_button)
        upload_button.click()
        
        # Wait for upload completion - look for the chain table or NGL viewer
        # This is the universal indicator that upload is complete
        WebDriverWait(self.driver, 120).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "chain-table")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".membrane-wide canvas")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'NGL Viewer')]"))
            )
        )
        
        # Verify upload was successful by checking for chain table
        from selenium.common import TimeoutException
        try:
            chain_table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "chain-table"))
            )
            
            # Wait for checkboxes to be available
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#chain-table input[type='checkbox']"))
            )
            
            print(f"✅ Successfully uploaded custom PDB file: {pdb_file_path.name}")
            
        except TimeoutException:
            # Check for error messages
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'failed')]")
            if error_elements:
                error_text = error_elements[0].text
                raise Exception(f"File upload failed: {error_text}")
            else:
                raise Exception("File upload completed but no chain table found")


if __name__ == "__main__":
    # Example for CUSTOM upload - using the test PDB file
    test_pdb_path = Path("/Users/sapelkinav/code/python/oprlm/tests/2W6V.pdb")

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

    try:
        oprlm_client = OprlmSeleniumClient()
        print("Initializing browser session...")
        oprlm_client.init_selenium_oprlm_session(headless=False)  # Set to True for headless
        
        print("Starting custom PDB upload...")
        oprlm_client.search_membrane_protein(file_request)
        print("File uploaded successfully!")
        
        print("Submitting job...")
        oprlm_client.submit_job(file_request)
        print("Job completed!")
        
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

