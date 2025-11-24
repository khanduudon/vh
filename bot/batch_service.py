"""
Batch file service for managing batch file operations
"""
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import hashlib

from bot.database import Database
from bot.extractor import ClassPlusExtractor
from bot.models import OrgCode, BatchFile, DownloadProgress
from bot.exceptions import (
    OrgCodeNotFoundError, BatchFileNotFoundError, 
    DownloadFailedError, StorageError
)
from bot.utils import (
    validate_org_code, sanitize_filename, 
    get_content_type, format_file_size
)
from bot.config import CACHE_ENABLED, CACHE_DIR, CACHE_TTL
from bot.logger import setup_logger, log_file_operation

logger = setup_logger(__name__)


class BatchService:
    """Service for batch file operations"""
    
    def __init__(self, db: Database = None, extractor: ClassPlusExtractor = None):
        """
        Initialize batch service
        
        Args:
            db: Database instance (creates new if None)
            extractor: ClassPlusExtractor instance (creates new if None)
        """
        self.db = db or Database()
        self.extractor = extractor or ClassPlusExtractor()
        self.cache_dir = CACHE_DIR if CACHE_ENABLED else None
    
    def fetch_batches_by_org_code(self, org_code: str, force_refresh: bool = False) -> List[BatchFile]:
        """
        Fetch all batch files for an organization code
        
        Args:
            org_code: Organization code
            force_refresh: If True, fetch from API even if cached
            
        Returns:
            List of BatchFile objects
            
        Raises:
            OrgCodeNotFoundError: If org code is invalid
        """
        # Validate org code
        validate_org_code(org_code)
        
        # Check if org exists in database and not forcing refresh
        if not force_refresh:
            cached_batches = self.db.get_batches_by_org_code(org_code)
            if cached_batches:
                logger.info(f"Returning {len(cached_batches)} cached batches for org {org_code}")
                return cached_batches
        
        # Fetch from ClassPlus API
        logger.info(f"Fetching batches from API for org {org_code}")
        batch_data_list = self.extractor.fetch_org_batches(org_code)
        
        # Create or update org code entry
        org = self.db.get_org_code(org_code)
        if not org:
            org = OrgCode(
                org_code=org_code,
                org_name=batch_data_list[0].get('org_name', org_code) if batch_data_list else org_code,
                batch_count=len(batch_data_list)
            )
            self.db.create_org_code(org)
        else:
            self.db.update_org_code(org_code, {
                'batch_count': len(batch_data_list),
                'updated_at': datetime.utcnow()
            })
        
        # Create BatchFile objects and store metadata
        batch_files = []
        for batch_data in batch_data_list:
            batch_file = BatchFile(
                batch_id=batch_data['batch_id'],
                org_code=org_code,
                batch_name=batch_data.get('batch_name', 'Unnamed Batch'),
                filename=sanitize_filename(batch_data.get('filename', f"{batch_data['batch_id']}.pdf")),
                metadata=batch_data
            )
            
            # Check if batch already exists
            existing = self.db.get_batch_file(batch_file.batch_id)
            if not existing:
                self.db.create_batch_file(batch_file)
            
            batch_files.append(batch_file)
        
        logger.info(f"Fetched {len(batch_files)} batches for org {org_code}")
        return batch_files
    
    def download_batch_file(self, batch_id: str, org_code: str) -> bytes:
        """
        Download a specific batch file
        
        Args:
            batch_id: Batch file ID
            org_code: Organization code
            
        Returns:
            File content as bytes
            
        Raises:
            BatchFileNotFoundError: If batch file not found
            DownloadFailedError: If download fails
        """
        # Check cache first
        if CACHE_ENABLED:
            cached_file = self._get_from_cache(batch_id)
            if cached_file:
                logger.info(f"Returning cached file for batch {batch_id}")
                return cached_file
        
        # Check GridFS
        batch_file = self.db.get_batch_file(batch_id)
        if batch_file and batch_file.file_id:
            file_data = self.db.get_file(batch_file.file_id)
            if file_data:
                logger.info(f"Retrieved file from GridFS for batch {batch_id}")
                # Update cache
                if CACHE_ENABLED:
                    self._save_to_cache(batch_id, file_data)
                return file_data
        
        # Download from ClassPlus
        logger.info(f"Downloading batch file {batch_id} from ClassPlus")
        
        # Get download URL
        download_url = self.extractor.fetch_batch_file_url(batch_id, org_code)
        
        # Download file content
        file_data = self.extractor.download_batch_content(download_url)
        
        if not file_data:
            raise DownloadFailedError(download_url, "Empty file content")
        
        # Store in GridFS
        if batch_file:
            file_id = self.db.store_file(
                file_data,
                batch_file.filename,
                metadata={'batch_id': batch_id, 'org_code': org_code}
            )
            
            # Update batch file metadata
            self.db.update_batch_file(batch_id, {
                'file_id': file_id,
                'file_size': len(file_data),
                'downloaded_at': datetime.utcnow()
            })
            
            log_file_operation(logger, 'downloaded', batch_file.filename, len(file_data))
        
        # Save to cache
        if CACHE_ENABLED:
            self._save_to_cache(batch_id, file_data)
        
        return file_data
    
    def download_all_batches(self, org_code: str, force_refresh: bool = False) -> DownloadProgress:
        """
        Download all batch files for an organization
        
        Args:
            org_code: Organization code
            force_refresh: If True, re-download even if files exist
            
        Returns:
            DownloadProgress object with download statistics
        """
        # Fetch batch list
        batches = self.fetch_batches_by_org_code(org_code, force_refresh)
        
        progress = DownloadProgress(total_files=len(batches))
        
        for batch in batches:
            try:
                # Skip if already downloaded and not forcing refresh
                if not force_refresh and batch.file_id and self.db.file_exists(batch.file_id):
                    logger.info(f"Batch {batch.batch_id} already downloaded, skipping")
                    progress.downloaded_files += 1
                    continue
                
                # Download file
                file_data = self.download_batch_file(batch.batch_id, org_code)
                
                progress.downloaded_files += 1
                progress.downloaded_bytes += len(file_data)
                
                logger.info(f"Downloaded batch {batch.batch_id} ({progress.downloaded_files}/{progress.total_files})")
                
            except Exception as e:
                logger.error(f"Failed to download batch {batch.batch_id}: {e}")
                progress.failed_files += 1
        
        progress.end_time = datetime.utcnow()
        
        logger.info(f"Download complete: {progress.downloaded_files} succeeded, {progress.failed_files} failed")
        return progress
    
    def get_batch_file_from_storage(self, batch_id: str) -> Optional[bytes]:
        """
        Retrieve batch file from storage (cache or GridFS)
        
        Args:
            batch_id: Batch file ID
            
        Returns:
            File content as bytes or None if not found
        """
        # Check cache
        if CACHE_ENABLED:
            cached_file = self._get_from_cache(batch_id)
            if cached_file:
                return cached_file
        
        # Check GridFS
        batch_file = self.db.get_batch_file(batch_id)
        if batch_file and batch_file.file_id:
            return self.db.get_file(batch_file.file_id)
        
        return None
    
    def delete_org_batches(self, org_code: str) -> bool:
        """
        Delete all batch files for an organization
        
        Args:
            org_code: Organization code
            
        Returns:
            True if successful
        """
        try:
            # Get all batches
            batches = self.db.get_batches_by_org_code(org_code)
            
            # Delete files from GridFS
            for batch in batches:
                if batch.file_id:
                    self.db.delete_file(batch.file_id)
                
                # Delete from cache
                if CACHE_ENABLED:
                    self._delete_from_cache(batch.batch_id)
            
            # Delete batch metadata
            self.db.delete_batches_by_org_code(org_code)
            
            # Delete org code
            self.db.delete_org_code(org_code)
            
            logger.info(f"Deleted all batches for org {org_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete batches for org {org_code}: {e}")
            raise StorageError("delete_org_batches", str(e))
    
    # ==================== Cache Methods ====================
    
    def _get_cache_path(self, batch_id: str) -> Path:
        """Get cache file path for batch ID"""
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{batch_id}.cache"
    
    def _get_from_cache(self, batch_id: str) -> Optional[bytes]:
        """Retrieve file from cache"""
        if not CACHE_ENABLED:
            return None
        
        cache_path = self._get_cache_path(batch_id)
        if cache_path and cache_path.exists():
            # Check if cache is still valid (TTL)
            age = datetime.utcnow().timestamp() - cache_path.stat().st_mtime
            if age < CACHE_TTL:
                with open(cache_path, 'rb') as f:
                    return f.read()
            else:
                # Cache expired, delete it
                cache_path.unlink()
        
        return None
    
    def _save_to_cache(self, batch_id: str, file_data: bytes):
        """Save file to cache"""
        if not CACHE_ENABLED:
            return
        
        cache_path = self._get_cache_path(batch_id)
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'wb') as f:
                f.write(file_data)
            logger.debug(f"Saved batch {batch_id} to cache")
    
    def _delete_from_cache(self, batch_id: str):
        """Delete file from cache"""
        if not CACHE_ENABLED:
            return
        
        cache_path = self._get_cache_path(batch_id)
        if cache_path and cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Deleted batch {batch_id} from cache")
