"""
API interface for batch file operations
"""
from typing import Dict, List, Optional
from datetime import datetime

from bot.batch_service import BatchService
from bot.models import BatchFileResponse, BatchFile
from bot.exceptions import (
    OrgCodeNotFoundError, BatchFileNotFoundError,
    DownloadFailedError, ValidationError
)
from bot.utils import validate_org_code, format_file_size
from bot.logger import setup_logger

logger = setup_logger(__name__)


class BatchFileAPI:
    """API interface for batch file operations"""
    
    def __init__(self, batch_service: BatchService = None):
        """
        Initialize API
        
        Args:
            batch_service: BatchService instance (creates new if None)
        """
        self.service = batch_service or BatchService()
    
    def get_batches_by_org_code(self, org_code: str, force_refresh: bool = False) -> Dict:
        """
        Get all batch files for an organization code
        
        Args:
            org_code: Organization code
            force_refresh: If True, fetch from API even if cached
            
        Returns:
            Dictionary with batch information
            
        Example response:
            {
                "success": True,
                "message": "Found 5 batches",
                "org_code": "ABC123",
                "org_name": "Example Org",
                "batch_count": 5,
                "batches": [
                    {
                        "batch_id": "batch_001",
                        "batch_name": "Batch 1",
                        "filename": "batch_001.pdf",
                        "file_size": 1024000,
                        "file_size_formatted": "1.00 MB",
                        "created_at": "2024-01-01T00:00:00",
                        "downloaded": True
                    },
                    ...
                ]
            }
        """
        try:
            # Validate org code
            validate_org_code(org_code)
            
            # Fetch batches
            batches = self.service.fetch_batches_by_org_code(org_code, force_refresh)
            
            # Get org info
            org = self.service.db.get_org_code(org_code)
            
            # Format batch data
            batch_list = []
            for batch in batches:
                batch_dict = {
                    'batch_id': batch.batch_id,
                    'batch_name': batch.batch_name,
                    'filename': batch.filename,
                    'file_size': batch.file_size,
                    'file_size_formatted': format_file_size(batch.file_size),
                    'content_type': batch.content_type,
                    'created_at': batch.created_at.isoformat() if batch.created_at else None,
                    'downloaded': batch.file_id is not None,
                    'downloaded_at': batch.downloaded_at.isoformat() if batch.downloaded_at else None
                }
                batch_list.append(batch_dict)
            
            response = BatchFileResponse(
                success=True,
                message=f"Found {len(batches)} batches",
                org_code=org_code,
                org_name=org.org_name if org else org_code,
                batch_count=len(batches),
                batches=batch_list
            )
            
            logger.info(f"API: Retrieved {len(batches)} batches for org {org_code}")
            return response.to_dict()
            
        except OrgCodeNotFoundError as e:
            logger.warning(f"API: Org code not found: {org_code}")
            return BatchFileResponse(
                success=False,
                message=str(e),
                errors=[{'type': 'OrgCodeNotFoundError', 'message': str(e)}]
            ).to_dict()
            
        except ValidationError as e:
            logger.warning(f"API: Validation error: {e}")
            return BatchFileResponse(
                success=False,
                message=str(e),
                errors=[{'type': 'ValidationError', 'message': str(e)}]
            ).to_dict()
            
        except Exception as e:
            logger.error(f"API: Unexpected error: {e}")
            return BatchFileResponse(
                success=False,
                message="An unexpected error occurred",
                errors=[{'type': type(e).__name__, 'message': str(e)}]
            ).to_dict()
    
    def download_batch(self, batch_id: str, org_code: str) -> Dict:
        """
        Download a specific batch file
        
        Args:
            batch_id: Batch file ID
            org_code: Organization code
            
        Returns:
            Dictionary with file data and metadata
            
        Example response:
            {
                "success": True,
                "message": "File downloaded successfully",
                "batch_id": "batch_001",
                "filename": "batch_001.pdf",
                "file_size": 1024000,
                "file_size_formatted": "1.00 MB",
                "content_type": "application/pdf",
                "file_data": b"..." # bytes
            }
        """
        try:
            # Download file
            file_data = self.service.download_batch_file(batch_id, org_code)
            
            # Get batch metadata
            batch = self.service.db.get_batch_file(batch_id)
            
            if not batch:
                raise BatchFileNotFoundError(batch_id, org_code)
            
            response = {
                'success': True,
                'message': 'File downloaded successfully',
                'batch_id': batch_id,
                'filename': batch.filename,
                'file_size': len(file_data),
                'file_size_formatted': format_file_size(len(file_data)),
                'content_type': batch.content_type,
                'file_data': file_data
            }
            
            logger.info(f"API: Downloaded batch {batch_id} ({format_file_size(len(file_data))})")
            return response
            
        except BatchFileNotFoundError as e:
            logger.warning(f"API: Batch file not found: {batch_id}")
            return {
                'success': False,
                'message': str(e),
                'errors': [{'type': 'BatchFileNotFoundError', 'message': str(e)}]
            }
            
        except DownloadFailedError as e:
            logger.error(f"API: Download failed for batch {batch_id}: {e}")
            return {
                'success': False,
                'message': str(e),
                'errors': [{'type': 'DownloadFailedError', 'message': str(e)}]
            }
            
        except Exception as e:
            logger.error(f"API: Unexpected error downloading batch {batch_id}: {e}")
            return {
                'success': False,
                'message': "An unexpected error occurred",
                'errors': [{'type': type(e).__name__, 'message': str(e)}]
            }
    
    def sync_org_batches(self, org_code: str, force_refresh: bool = False) -> Dict:
        """
        Sync all batches for an organization (fetch metadata and download files)
        
        Args:
            org_code: Organization code
            force_refresh: If True, re-download even if files exist
            
        Returns:
            Dictionary with sync status
            
        Example response:
            {
                "success": True,
                "message": "Sync completed",
                "org_code": "ABC123",
                "total_files": 5,
                "downloaded_files": 5,
                "failed_files": 0,
                "total_bytes": 5120000,
                "total_bytes_formatted": "5.00 MB",
                "progress_percentage": 100.0,
                "duration_seconds": 12.5
            }
        """
        try:
            # Validate org code
            validate_org_code(org_code)
            
            # Download all batches
            progress = self.service.download_all_batches(org_code, force_refresh)
            
            # Calculate duration
            duration = 0
            if progress.start_time and progress.end_time:
                duration = (progress.end_time - progress.start_time).total_seconds()
            
            response = {
                'success': True,
                'message': 'Sync completed',
                'org_code': org_code,
                'total_files': progress.total_files,
                'downloaded_files': progress.downloaded_files,
                'failed_files': progress.failed_files,
                'total_bytes': progress.downloaded_bytes,
                'total_bytes_formatted': format_file_size(progress.downloaded_bytes),
                'progress_percentage': progress.progress_percentage,
                'duration_seconds': duration
            }
            
            logger.info(f"API: Synced org {org_code} - {progress.downloaded_files}/{progress.total_files} files")
            return response
            
        except OrgCodeNotFoundError as e:
            logger.warning(f"API: Org code not found: {org_code}")
            return {
                'success': False,
                'message': str(e),
                'errors': [{'type': 'OrgCodeNotFoundError', 'message': str(e)}]
            }
            
        except ValidationError as e:
            logger.warning(f"API: Validation error: {e}")
            return {
                'success': False,
                'message': str(e),
                'errors': [{'type': 'ValidationError', 'message': str(e)}]
            }
            
        except Exception as e:
            logger.error(f"API: Unexpected error syncing org {org_code}: {e}")
            return {
                'success': False,
                'message': "An unexpected error occurred",
                'errors': [{'type': type(e).__name__, 'message': str(e)}]
            }
    
    def get_batch_info(self, batch_id: str) -> Dict:
        """
        Get information about a specific batch file
        
        Args:
            batch_id: Batch file ID
            
        Returns:
            Dictionary with batch information
        """
        try:
            batch = self.service.db.get_batch_file(batch_id)
            
            if not batch:
                raise BatchFileNotFoundError(batch_id)
            
            response = {
                'success': True,
                'message': 'Batch file found',
                'batch': {
                    'batch_id': batch.batch_id,
                    'org_code': batch.org_code,
                    'batch_name': batch.batch_name,
                    'filename': batch.filename,
                    'file_size': batch.file_size,
                    'file_size_formatted': format_file_size(batch.file_size),
                    'content_type': batch.content_type,
                    'created_at': batch.created_at.isoformat() if batch.created_at else None,
                    'downloaded': batch.file_id is not None,
                    'downloaded_at': batch.downloaded_at.isoformat() if batch.downloaded_at else None,
                    'metadata': batch.metadata
                }
            }
            
            return response
            
        except BatchFileNotFoundError as e:
            logger.warning(f"API: Batch file not found: {batch_id}")
            return {
                'success': False,
                'message': str(e),
                'errors': [{'type': 'BatchFileNotFoundError', 'message': str(e)}]
            }
            
        except Exception as e:
            logger.error(f"API: Unexpected error getting batch info {batch_id}: {e}")
            return {
                'success': False,
                'message': "An unexpected error occurred",
                'errors': [{'type': type(e).__name__, 'message': str(e)}]
            }
