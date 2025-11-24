"""
Unit tests for batch service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from bot.batch_service import BatchService
from bot.models import OrgCode, BatchFile, DownloadProgress
from bot.exceptions import OrgCodeNotFoundError, BatchFileNotFoundError


class TestBatchService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.mock_extractor = Mock()
        self.service = BatchService(db=self.mock_db, extractor=self.mock_extractor)
    
    def test_fetch_batches_by_valid_org_code(self):
        """Test fetching batches with a valid org code"""
        org_code = "ABC123"
        
        # Mock API response
        self.mock_extractor.fetch_org_batches.return_value = [
            {
                'batch_id': 'batch_001',
                'batch_name': 'Batch 1',
                'filename': 'batch_001.pdf',
                'org_name': 'Test Org'
            }
        ]
        
        # Mock database responses
        self.mock_db.get_org_code.return_value = None
        self.mock_db.get_batch_file.return_value = None
        
        # Execute
        batches = self.service.fetch_batches_by_org_code(org_code)
        
        # Assert
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].batch_id, 'batch_001')
        self.mock_extractor.fetch_org_batches.assert_called_once_with(org_code)
    
    def test_fetch_batches_by_invalid_org_code(self):
        """Test fetching batches with an invalid org code"""
        org_code = "INVALID"
        
        # Mock API to raise exception
        self.mock_extractor.fetch_org_batches.side_effect = OrgCodeNotFoundError(org_code)
        
        # Execute and assert
        with self.assertRaises(OrgCodeNotFoundError):
            self.service.fetch_batches_by_org_code(org_code)
    
    def test_download_batch_file_from_api(self):
        """Test downloading a batch file from API"""
        batch_id = "batch_001"
        org_code = "ABC123"
        file_data = b"test file content"
        
        # Mock responses
        self.mock_db.get_batch_file.return_value = BatchFile(
            batch_id=batch_id,
            org_code=org_code,
            batch_name="Test Batch",
            filename="test.pdf"
        )
        self.mock_db.get_file.return_value = None  # Not in GridFS
        self.mock_extractor.fetch_batch_file_url.return_value = "http://example.com/file.pdf"
        self.mock_extractor.download_batch_content.return_value = file_data
        self.mock_db.store_file.return_value = "file_id_123"
        
        # Execute
        result = self.service.download_batch_file(batch_id, org_code)
        
        # Assert
        self.assertEqual(result, file_data)
        self.mock_extractor.download_batch_content.assert_called_once()
        self.mock_db.store_file.assert_called_once()
    
    def test_download_all_batches(self):
        """Test downloading all batches for an org"""
        org_code = "ABC123"
        
        # Mock batches
        batches = [
            BatchFile(
                batch_id=f"batch_{i}",
                org_code=org_code,
                batch_name=f"Batch {i}",
                filename=f"batch_{i}.pdf"
            )
            for i in range(3)
        ]
        
        # Mock responses
        with patch.object(self.service, 'fetch_batches_by_org_code', return_value=batches):
            with patch.object(self.service, 'download_batch_file', return_value=b"test"):
                self.mock_db.file_exists.return_value = False
                
                # Execute
                progress = self.service.download_all_batches(org_code)
                
                # Assert
                self.assertEqual(progress.total_files, 3)
                self.assertEqual(progress.downloaded_files, 3)
                self.assertEqual(progress.failed_files, 0)
    
    def test_get_batch_file_from_storage(self):
        """Test retrieving batch file from storage"""
        batch_id = "batch_001"
        file_data = b"test file content"
        
        # Mock responses
        self.mock_db.get_batch_file.return_value = BatchFile(
            batch_id=batch_id,
            org_code="ABC123",
            batch_name="Test Batch",
            filename="test.pdf",
            file_id="file_id_123"
        )
        self.mock_db.get_file.return_value = file_data
        
        # Execute
        result = self.service.get_batch_file_from_storage(batch_id)
        
        # Assert
        self.assertEqual(result, file_data)
        self.mock_db.get_file.assert_called_once_with("file_id_123")
    
    def test_delete_org_batches(self):
        """Test deleting all batches for an org"""
        org_code = "ABC123"
        
        # Mock batches
        batches = [
            BatchFile(
                batch_id="batch_001",
                org_code=org_code,
                batch_name="Batch 1",
                filename="batch_001.pdf",
                file_id="file_id_1"
            )
        ]
        
        # Mock responses
        self.mock_db.get_batches_by_org_code.return_value = batches
        self.mock_db.delete_file.return_value = True
        self.mock_db.delete_batches_by_org_code.return_value = 1
        self.mock_db.delete_org_code.return_value = True
        
        # Execute
        result = self.service.delete_org_batches(org_code)
        
        # Assert
        self.assertTrue(result)
        self.mock_db.delete_file.assert_called_once_with("file_id_1")
        self.mock_db.delete_batches_by_org_code.assert_called_once_with(org_code)
        self.mock_db.delete_org_code.assert_called_once_with(org_code)


if __name__ == "__main__":
    unittest.main()
