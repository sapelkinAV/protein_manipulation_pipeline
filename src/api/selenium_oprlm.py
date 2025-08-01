from enum import Enum
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

PROTEIN_STRUCTURE_FIELD_NAME = "fileInputMode"
MEMBRANE_TYPE_FIELD_NAME = "membraneType"

class ProteinStructure(Enum):
    RCSB = "searchPDB"  # RCSB
    OPRLM = "searchOPM"  # OPRLM
    CUSTOM = "upload"  # CUSTOM

class MembraneType(Enum):
    CUSTOM = "custom"  # Simple model membrane
    PM_MAMMALIAN = "PMm"  # Plasma membrane (mammalian)
    PM_PLANTS = "PMp"  # Plasma membrane (plants)
    PM_FUNGI = "PMf"  # Plasma membrane (Fungi)
    ER_FUNGI = "ERf"  # ER (fungi)
    ER_MAMMALIAN = "ERm"  # ER (mammalian)
    GOLGI_MAMMALIAN = "GOLm"  # Golgi membrane (mammalian)
    GOLGI_FUNGI = "GOLf"  # Golgi membrane (fungi)
    ENDOSOME_MAMMALIAN = "ENDm"  # Endosome membrane (mammalian)
    LYSOSOME_MAMMALIAN = "LYSm"  # Lysosome membrane (mammalian)
    OUTER_MITOCHONDRIAL = "MOM"  # Outer mitochondrial membrane
    INNER_MITOCHONDRIAL = "MIM"  # Inner mitochondrial membrane
    VACUOLE = "VAC" # Vacuole membrane
    THYLACOID_PLANTS = "TPp" # Thylakoid membrane (plants)
    THYLACOID_BACTERIA = "TPb" # Thylakoid membrane (bacteria)
    ARCHEBACTERIA = "aPM" # Archaebacteria cell membrane
    GRAM_NEGATIVE_BACTERIA_OUTER_MEMBRANE = "G-OM" # Gram-negative bacteria outer membrane
    GRAM_NEGATIVE_BACTERIA_INNER_MEMBRANE = "G-IM" # Gram-negative bacteria inner membrane
    GRAM_POSITIVE_BACTERIA_MEMBRANE = "G-IM" # Gram-positive bacteria membrane

class ProteinTopologyMembrane(Enum):
    IN = "in"
    OUT = "out"

class MembraneConfig:
    def __init__(self,
                 membrane_type: MembraneType = MembraneType.CUSTOM,
                 # OPRLM FOR SIMPLE MEMBRANE
                 popc: bool = True,
                 dopc: bool = False,
                 dspc: bool = False,
                 dmpc: bool = False,
                 dppc: bool = False,
                 chol_value: float = 20.0,
                 # RCSB AND UPLOAD
                 protein_topology: ProteinTopologyMembrane = ProteinTopologyMembrane.IN
                 ):
        self.membrane_type = membrane_type
        self.popc = popc
        self.dopc = dopc
        self.dspc = dspc
        self.dmpc = dmpc
        self.dppc = dppc
        self.chol_value = chol_value
        self.protein_topology = protein_topology

class PdbFileOptionRequest:
    def __init__(self,
                 pdb_id: str,
                 file_input_mode: ProteinStructure,
                 file_path: Path = None,
                 email: str = None,
                 membrane_config: MembraneConfig = None,
                 ):
        self.pdb_id = pdb_id
        self.file_input_mode = file_input_mode
        self.file_path = file_path
        self.output_dir = Path(f"/Users/sapelkinav/code/python/oprlm/data/pdb/step1_output/{pdb_id}")
        self.email = email
        self.membrane_config = membrane_config or MembraneConfig()

class OprlmSeleniumClient:

    def __init__(self):
        self.driver = None

    def init_selenium_oprlm_session(self, headless=True):
        chrome_options = self.get_default_chrome_options()
        if headless:
            chrome_options.add_argument("--headless")

        # Use ChromeDriverManager to automatically manage the ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.driver.get("https://oprlm.org/oprlm_server")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )


    def search_membrane_protein(self, pdb_file_request: PdbFileOptionRequest):
        #Pick
        self.__select_protein_structure(pdb_file_request.file_input_mode)

        if pdb_file_request.file_input_mode == ProteinStructure.RCSB or pdb_file_request.file_input_mode == ProteinStructure.OPRLM:
            search_box = self.driver.find_element(By.ID, "search-box")
            search_box.clear()
            search_box.send_keys(pdb_file_request.pdb_id)
            # Click the search button specifically within the api-search div
            search_button = self.driver.find_element(By.CSS_SELECTOR,
                                              "div.api-search span.submit-button")
            search_button.click()
            
            # Wait for search results to load
            # Wait for either the chain-table to appear (success) or error message
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: (
                        len(driver.find_elements(By.ID, "chain-table")) > 0 or
                        len(driver.find_elements(By.XPATH, "//*[contains(text(), 'PDB entry was not found') or contains(text(), 'not found')]")) > 0
                    )
                )
                
                # Check if we got results
                if len(self.driver.find_elements(By.ID, "chain-table")) > 0:
                    print(f"Search completed successfully for {pdb_file_request.pdb_id}")
                    # Wait for chains to be visible
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#chain-table input[type='checkbox']"))
                    )
                else:
                    error_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'PDB entry was not found') or contains(text(), 'not found')]").text
                    raise Exception(f"Search failed: {error_text}")
                    
            except Exception as e:
                print(f"Search timeout or error for {pdb_file_request.pdb_id}: {e}")
                raise
        else:
            pass

    def submit_job(self, pdb_file_request: PdbFileOptionRequest):

        # Fill membrane configuration based on MembraneConfig

        # Fill composition checkboxes
        if pdb_file_request.membrane_config is not None:
            self.__set_checkbox_value("popc", pdb_file_request.membrane_config.popc)
            self.__set_checkbox_value("dopc", pdb_file_request.membrane_config.dopc)
            self.__set_checkbox_value("dspc", pdb_file_request.membrane_config.dspc)
            self.__set_checkbox_value("dmpc", pdb_file_request.membrane_config.dmpc)
            self.__set_checkbox_value("dppc", pdb_file_request.membrane_config.dppc)

            custom_chol = self.driver.find_element(By.NAME, "customChol")
            custom_chol.clear()
            custom_chol.send_keys(str(pdb_file_request.membrane_config.chol_value))

        # Fill email and submit job
        email_box = self.driver.find_element(By.ID, "userEmail")
        email_box.clear()
        email_box.send_keys(pdb_file_request.email or "abobus@gmail.com")
        
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
        self.__select_dropdown_value(MEMBRANE_TYPE_FIELD_NAME, membrane_config.membrane_type.value)

        # FOR OPRLM AND RCSB Simple membrane type
        if ((protein_structure == ProteinStructure.OPRLM or ProteinStructure.RCSB)
                and membrane_config.membrane_type == MembraneType.CUSTOM):
            self.__set_checkbox_value("popc", membrane_config.popc)
            self.__set_checkbox_value("dopc", membrane_config.dopc)
            self.__set_checkbox_value("dspc", membrane_config.dspc)
            self.__set_checkbox_value("dmpc", membrane_config.dmpc)
            self.__set_checkbox_value("dppc", membrane_config.dppc)

            custom_chol = self.driver.find_element(By.NAME, "customChol")
            custom_chol.clear()
            custom_chol.send_keys(str(membrane_config.chol_value))
            return

        # FOR EVERYTHING ELSE
        if membrane_config is not None:
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


if __name__ == "__main__":
    file_request = PdbFileOptionRequest(
        pdb_id="3c02",
        file_input_mode=ProteinStructure.OPRLM,
        membrane_config=MembraneConfig(True, True, True, True, True, 30.0),
    )
    oprlm_client = OprlmSeleniumClient()
    oprlm_client.init_selenium_oprlm_session(headless=False)  # Set to False for interactive mode
    oprlm_client.search_membrane_protein(file_request)
    oprlm_client.submit_job(file_request)

