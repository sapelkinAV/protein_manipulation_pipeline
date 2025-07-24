from enum import Enum
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
# Use webdriver-manager for automatic ChromeDriver management
from webdriver_manager.chrome import ChromeDriverManager


class FileInputMode(Enum):
    RCMB = "searchPDB"  # RCSB
    OPRLM = "searchOPM"  # OPRLM
    CUSTOM = "upload"  # CUSTOM

class PdbFileOptionRequest:
    def __init__(self,
                 pdb_id: str,
                 file_input_mode: FileInputMode,
                 file_path: Path = None,
                 email: str = None,
                 ):
        self.pdb_id = pdb_id
        self.file_input_mode = file_input_mode
        self.file_path = file_path
        self.output_dir = Path(f"/Users/sapelkinav/code/python/oprlm/data/pdb/step1_output/{pdb_id}")
        self.email = email

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
        oprlm_file_mode = self.driver.find_element(By.NAME, "fileInputMode")

        dropdown = Select(oprlm_file_mode)
        dropdown.select_by_value(pdb_file_request.file_input_mode.value)

        if pdb_file_request.file_input_mode == FileInputMode.RCMB or pdb_file_request.file_input_mode == FileInputMode.OPRLM:
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

        # Use output_dir from PdbFileOptionRequest or create default
        download_dir = pdb_file_request.output_dir
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Fill email and submit job
        email_box = self.driver.find_element(By.ID, "userEmail")
        email_box.clear()
        email_box.send_keys(pdb_file_request.email or "al.vi.sapelkin@gmail.com")
        
        submit_button = self.driver.find_element(By.ID, "submit")
        submit_button.click()
        
        print("Job submitted, waiting for completion...")
        
        # Wait for job completion and download links
        WebDriverWait(self.driver, 3600).until(
            EC.presence_of_element_located((By.ID, "download_pdb"))
        )
        
        print("Job completed! Downloading files...")
        
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


if __name__ == "__main__":
    file_request = PdbFileOptionRequest(
        pdb_id="3c02",
        file_input_mode=FileInputMode.OPRLM
    )
    oprlm_client = OprlmSeleniumClient()
    oprlm_client.init_selenium_oprlm_session(headless=True)  # Set to False for interactive mode
    oprlm_client.search_membrane_protein(file_request)
    oprlm_client.submit_job(file_request)

