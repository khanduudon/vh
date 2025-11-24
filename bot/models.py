"""
Data models for the ClassPlus Batch File Extractor
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class OrgCode:
    """Represents an organization in ClassPlus"""
    org_code: str
    org_name: str
    batch_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'org_code': self.org_code,
            'org_name': self.org_name,
            'batch_count': self.batch_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OrgCode':
        """Create instance from dictionary"""
        return cls(
            org_code=data['org_code'],
            org_name=data['org_name'],
            batch_count=data.get('batch_count', 0),
            created_at=data.get('created_at', datetime.utcnow()),
            updated_at=data.get('updated_at', datetime.utcnow()),
            metadata=data.get('metadata', {})
        )


@dataclass
class BatchFile:
    """Represents a batch file with metadata"""
    batch_id: str
    org_code: str
    batch_name: str
    filename: str
    file_size: int = 0
    content_type: str = 'application/octet-stream'
    file_id: Optional[str] = None  # GridFS file ID
    created_at: datetime = field(default_factory=datetime.utcnow)
    downloaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'batch_id': self.batch_id,
            'org_code': self.org_code,
            'batch_name': self.batch_name,
            'filename': self.filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'file_id': self.file_id,
            'created_at': self.created_at,
            'downloaded_at': self.downloaded_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BatchFile':
        """Create instance from dictionary"""
        return cls(
            batch_id=data['batch_id'],
            org_code=data['org_code'],
            batch_name=data['batch_name'],
            filename=data['filename'],
            file_size=data.get('file_size', 0),
            content_type=data.get('content_type', 'application/octet-stream'),
            file_id=data.get('file_id'),
            created_at=data.get('created_at', datetime.utcnow()),
            downloaded_at=data.get('downloaded_at'),
            metadata=data.get('metadata', {})
        )


@dataclass
class BatchFileResponse:
    """Response model for batch file operations"""
    success: bool
    message: str
    org_code: Optional[str] = None
    org_name: Optional[str] = None
    batch_count: int = 0
    batches: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        response = {
            'success': self.success,
            'message': self.message
        }
        
        if self.org_code:
            response['org_code'] = self.org_code
        if self.org_name:
            response['org_name'] = self.org_name
        if self.batch_count > 0:
            response['batch_count'] = self.batch_count
        if self.batches:
            response['batches'] = [
                b.to_dict() if isinstance(b, BatchFile) else b 
                for b in self.batches
            ]
        if self.errors:
            response['errors'] = self.errors
            
        return response


@dataclass
class DownloadProgress:
    """Track download progress for batch files"""
    total_files: int
    downloaded_files: int = 0
    failed_files: int = 0
    total_bytes: int = 0
    downloaded_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.downloaded_files / self.total_files) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if download is complete"""
        return (self.downloaded_files + self.failed_files) >= self.total_files
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_files': self.total_files,
            'downloaded_files': self.downloaded_files,
            'failed_files': self.failed_files,
            'total_bytes': self.total_bytes,
            'downloaded_bytes': self.downloaded_bytes,
            'progress_percentage': self.progress_percentage,
            'is_complete': self.is_complete,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
