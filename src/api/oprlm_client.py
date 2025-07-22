import asyncio
import aiohttp
from typing import Optional, Dict, Any
from pathlib import Path
import json
from urllib.parse import urljoin


class OPRLMClient:
    """Client for interacting with OPRLM server API."""
    
    def __init__(self, base_url: str = "https://oprlm.org/oprlm_server"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def download_pdb(self, pdb_id: str, output_path: Path) -> bool:
        """Download PDB file from OPRLM static files."""
        url = f"https://oprlm.org/static/{pdb_id}.pdb"
        
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
            print(f"Error downloading PDB {pdb_id}: {e}")
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