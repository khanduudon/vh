"""
Database layer for MongoDB operations and GridFS file storage
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
from gridfs import GridFS
from bson import ObjectId

from bot.config import MONGODB_URI, DATABASE_NAME, COLLECTION_ORG_CODES, COLLECTION_BATCH_FILES
from bot.models import OrgCode, BatchFile
from bot.exceptions import StorageError
from bot.logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """Database manager for MongoDB and GridFS operations"""
    
    def __init__(self, uri: str = MONGODB_URI, db_name: str = DATABASE_NAME):
        """
        Initialize database connection
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        try:
            # Add SSL/TLS settings to fix connection issues on Render.com
            self.client = MongoClient(
                uri,
                tlsAllowInvalidCertificates=True,  # Fix SSL handshake issues
                serverSelectionTimeoutMS=5000,     # Faster timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            self.db = self.client[db_name]
            self.fs = GridFS(self.db)
            
            # Collections
            self.org_codes = self.db[COLLECTION_ORG_CODES]
            self.batch_files = self.db[COLLECTION_BATCH_FILES]
            
            # Create indexes (with error handling)
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {db_name}")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise StorageError("database_connection", str(e))
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Org codes indexes
            self.org_codes.create_index([("org_code", ASCENDING)], unique=True)
            
            # Batch files indexes
            self.batch_files.create_index([("batch_id", ASCENDING)], unique=True)
            self.batch_files.create_index([("org_code", ASCENDING)])
            self.batch_files.create_index([("org_code", ASCENDING), ("batch_id", ASCENDING)])
            
            logger.debug("Database indexes created successfully")
        except PyMongoError as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    # ==================== Org Code Operations ====================
    
    def create_org_code(self, org_code: OrgCode) -> str:
        """
        Create a new organization code entry
        
        Args:
            org_code: OrgCode instance
            
        Returns:
            Inserted document ID
        """
        try:
            result = self.org_codes.insert_one(org_code.to_dict())
            logger.info(f"Created org code: {org_code.org_code}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to create org code {org_code.org_code}: {e}")
            raise StorageError("create_org_code", str(e))
    
    def get_org_code(self, org_code: str) -> Optional[OrgCode]:
        """
        Retrieve organization by code
        
        Args:
            org_code: Organization code
            
        Returns:
            OrgCode instance or None if not found
        """
        try:
            doc = self.org_codes.find_one({"org_code": org_code})
            if doc:
                return OrgCode.from_dict(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Failed to get org code {org_code}: {e}")
            raise StorageError("get_org_code", str(e))
    
    def update_org_code(self, org_code: str, updates: Dict[str, Any]) -> bool:
        """
        Update organization code entry
        
        Args:
            org_code: Organization code
            updates: Dictionary of fields to update
            
        Returns:
            True if updated, False otherwise
        """
        try:
            updates['updated_at'] = datetime.utcnow()
            result = self.org_codes.update_one(
                {"org_code": org_code},
                {"$set": updates}
            )
            if result.modified_count > 0:
                logger.info(f"Updated org code: {org_code}")
                return True
            return False
        except PyMongoError as e:
            logger.error(f"Failed to update org code {org_code}: {e}")
            raise StorageError("update_org_code", str(e))
    
    def delete_org_code(self, org_code: str) -> bool:
        """
        Delete organization code entry
        
        Args:
            org_code: Organization code
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.org_codes.delete_one({"org_code": org_code})
            if result.deleted_count > 0:
                logger.info(f"Deleted org code: {org_code}")
                return True
            return False
        except PyMongoError as e:
            logger.error(f"Failed to delete org code {org_code}: {e}")
            raise StorageError("delete_org_code", str(e))
    
    # ==================== Batch File Operations ====================
    
    def create_batch_file(self, batch_file: BatchFile) -> str:
        """
        Create a new batch file entry
        
        Args:
            batch_file: BatchFile instance
            
        Returns:
            Inserted document ID
        """
        try:
            result = self.batch_files.insert_one(batch_file.to_dict())
            logger.info(f"Created batch file: {batch_file.batch_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to create batch file {batch_file.batch_id}: {e}")
            raise StorageError("create_batch_file", str(e))
    
    def get_batch_file(self, batch_id: str) -> Optional[BatchFile]:
        """
        Retrieve batch file by ID
        
        Args:
            batch_id: Batch file ID
            
        Returns:
            BatchFile instance or None if not found
        """
        try:
            doc = self.batch_files.find_one({"batch_id": batch_id})
            if doc:
                return BatchFile.from_dict(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Failed to get batch file {batch_id}: {e}")
            return None
    
    def get_batches_by_org_code(self, org_code: str) -> List[BatchFile]:
        """
        Get all batch files for an organization code from database
        
        Args:
            org_code: Organization code
            
        Returns:
            List of BatchFile objects
        """
        try:
            cursor = self.batch_files.find({"org_code": org_code})
            batches = []
            for doc in cursor:
                batches.append(BatchFile.from_dict(doc))
            logger.info(f"Retrieved {len(batches)} batches for org {org_code} from database")
            return batches
        except PyMongoError as e:
            # If database fails, return empty list (will fetch from API instead)
            logger.warning(f"Failed to get batches for org {org_code} from database: {e}")
            return []
    
    def update_batch_file(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update batch file entry
        
        Args:
            batch_id: Batch file ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated, False otherwise
        """
        try:
            result = self.batch_files.update_one(
                {"batch_id": batch_id},
                {"$set": updates}
            )
            if result.modified_count > 0:
                logger.info(f"Updated batch file: {batch_id}")
                return True
            return False
        except PyMongoError as e:
            logger.error(f"Failed to update batch file {batch_id}: {e}")
            raise StorageError("update_batch_file", str(e))
    
    def delete_batch_file(self, batch_id: str) -> bool:
        """
        Delete batch file entry
        
        Args:
            batch_id: Batch file ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.batch_files.delete_one({"batch_id": batch_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted batch file: {batch_id}")
                return True
            return False
        except PyMongoError as e:
            logger.error(f"Failed to delete batch file {batch_id}: {e}")
            raise StorageError("delete_batch_file", str(e))
    
    def delete_batches_by_org_code(self, org_code: str) -> int:
        """
        Delete all batch files for an organization
        
        Args:
            org_code: Organization code
            
        Returns:
            Number of deleted batch files
        """
        try:
            result = self.batch_files.delete_many({"org_code": org_code})
            count = result.deleted_count
            logger.info(f"Deleted {count} batch files for org {org_code}")
            return count
        except PyMongoError as e:
            logger.error(f"Failed to delete batches for org {org_code}: {e}")
            raise StorageError("delete_batches_by_org_code", str(e))
    
    # ==================== GridFS File Operations ====================
    
    def store_file(self, file_data: bytes, filename: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store file in GridFS
        
        Args:
            file_data: File content as bytes
            filename: Name of the file
            metadata: Optional metadata dictionary
            
        Returns:
            GridFS file ID
        """
        try:
            file_id = self.fs.put(
                file_data,
                filename=filename,
                metadata=metadata or {}
            )
            logger.info(f"Stored file in GridFS: {filename} (ID: {file_id})")
            return str(file_id)
        except PyMongoError as e:
            logger.error(f"Failed to store file {filename}: {e}")
            raise StorageError("store_file", str(e))
    
    def get_file(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve file from GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            grid_out = self.fs.get(ObjectId(file_id))
            file_data = grid_out.read()
            logger.info(f"Retrieved file from GridFS: {file_id}")
            return file_data
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            self.fs.delete(ObjectId(file_id))
            logger.info(f"Deleted file from GridFS: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    def file_exists(self, file_id: str) -> bool:
        """
        Check if file exists in GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return self.fs.exists(ObjectId(file_id))
        except Exception:
            return False
    
    # ==================== Utility Methods ====================
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
