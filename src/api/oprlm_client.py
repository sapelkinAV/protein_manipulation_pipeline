import asyncio
import aiohttp
import re
from typing import Optional, Dict, Any
from pathlib import Path
import json
from urllib.parse import urljoin


class OPRLMClient:
    """Client for interacting with OPRLM server API."""
    
    def __init__(self, base_url: str = "https://opm-back.cc.lehigh.edu/opm-backend", ssl_verify: bool = True):
        self.base_url = base_url.rstrip('/')
        self.ssl_verify = ssl_verify
        self.session: Optional[aiohttp.ClientSession] = None
        self.ssl_context = None
        
        if not ssl_verify:
            import ssl
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl=self.ssl_context) if self.ssl_context else None
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context) if self.ssl_context else None
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def submit_membrane_query(self, pdb_id: str, **kwargs) -> Optional[str]:
        """Submit membrane system query to OPRLM server."""
        url = urljoin(self.base_url, "submit")
        
        await self._ensure_session()
        
        # Parameters for membrane system processing
        params = {
            'pdb_id': pdb_id,
            'membrane_system': 'true',
            'orient': 'true',
            **kwargs
        }
        
        try:
            async with self.session.post(url, data=params) as response:
                if response.status == 200:
                    content = await response.text()
                    try:
                        result = json.loads(content)
                        return result.get('job_id')
                    except json.JSONDecodeError:
                        # Handle HTML response
                        if 'job_id' in content or 'task_id' in content:
                            # Extract job ID from HTML or text
                            import re
                            job_match = re.search(r'(?:job_id|task_id)\s*:\s*([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
                            if not job_match:
                                job_match = re.search(r'Job ID\s*:\s*([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
                            if job_match:
                                return job_match.group(1)
                        return None
                else:
                    return None
        except Exception as e:
            print(f"Error submitting membrane query: {e}")
            return None
    
    async def get_query_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get result of membrane system query."""
        url = urljoin(self.base_url, f"result/{job_id}")
        
        await self._ensure_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # Return a basic status dict for non-JSON responses
                        return {"status": "completed", "raw_content": content}
                else:
                    return None
        except Exception as e:
            print(f"Error getting query result: {e}")
            return None
    
    async def download_membrane_result(self, job_id: str, output_path: Path) -> bool:
        """Download membrane system result file."""
        url = urljoin(self.base_url, f"download/{job_id}")
        
        await self._ensure_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    output_path.write_text(content)
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Error downloading membrane result: {e}")
            return False
    
    async def process_membrane_system(self, pdb_id: str, output_path: Path,
                                    poll_interval: float = 2.0, timeout: float = 300.0,
                                    **query_params) -> bool:
        """Complete membrane system workflow: submit query, wait, download."""
        job_id = await self.submit_membrane_query(pdb_id, **query_params)
        if not job_id:
            return False
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                print("Membrane system processing timed out")
                return False
            
            status = await self.get_query_result(job_id)
            if not status:
                return False
            
            job_status = status.get('status')
            if job_status == 'completed':
                return await self.download_membrane_result(job_id, output_path)
            elif job_status in ['failed', 'error']:
                print(f"Membrane system processing failed: {status.get('error', 'Unknown error')}")
                return False
            
            await asyncio.sleep(poll_interval)
    
    async def download_pdb(self, pdb_id: str, output_path: Path) -> bool:
        """Download PDB file from verified sources."""
        # List of verified PDB sources in order of preference
        sources = [
            f"https://oprlm.org/static/{pdb_id}.pdb",
            f"https://files.rcsb.org/download/{pdb_id}.pdb",
            f"https://files.rcsb.org/download/{pdb_id}.pdb.gz",
        ]
        
        await self._ensure_session()
        
        for url in sources:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Validate PDB content
                        if "ATOM" in content or "HEADER" in content:
                            output_path.write_text(content)
                            return True
                        else:
                            # Try to handle gzipped content
                            if url.endswith('.gz'):
                                import gzip
                                try:
                                    # Handle gzipped PDB
                                    content = gzip.decompress(await response.read()).decode('utf-8')
                                    if "ATOM" in content or "HEADER" in content:
                                        output_path.write_text(content)
                                        return True
                                except:
                                    pass
                            
            except Exception as e:
                print(f"Error downloading from {url}: {e}")
                continue
        
        return False
    
    async def upload_pdb(self, pdb_file: Path) -> Optional[str]:
        """Upload PDB file to OPRLM orient endpoint."""
        url = urljoin(self.base_url, "orient")
        
        await self._ensure_session()
        
        try:
            with open(pdb_file, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=pdb_file.name)
                
                async with self.session.post(url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('job_id')
                    else:
                        return None
        except Exception as e:
            print(f"Error uploading PDB file: {e}")
            return None
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of orient job."""
        url = urljoin(self.base_url, f"job/{job_id}")
        
        await self._ensure_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception as e:
            print(f"Error checking job status: {e}")
            return None
    
    async def download_aligned_pdb(self, job_id: str, output_path: Path) -> bool:
        """Download aligned PDB file from completed job."""
        url = urljoin(self.base_url, f"job/{job_id}/download")
        
        await self._ensure_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    output_path.write_text(content)
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Error downloading aligned PDB: {e}")
            return False
    
    async def orient_pdb(self, pdb_file: Path, output_path: Path, 
                        poll_interval: float = 2.0, timeout: float = 300.0) -> bool:
        """Complete orient workflow: upload, wait, download."""
        job_id = await self.upload_pdb(pdb_file)
        if not job_id:
            return False
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                print("Orient job timed out")
                return False
            
            status = await self.get_job_status(job_id)
            if not status:
                return False
            
            job_status = status.get('status')
            if job_status == 'completed':
                return await self.download_aligned_pdb(job_id, output_path)
            elif job_status in ['failed', 'error']:
                print(f"Orient job failed: {status.get('error', 'Unknown error')}")
                return False
            
            await asyncio.sleep(poll_interval)