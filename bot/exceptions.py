"""
Custom exceptions for the ClassPlus Batch File Extractor
"""


class ExtractorBaseException(Exception):
    """Base exception for all extractor errors"""
    pass


class OrgCodeNotFoundError(ExtractorBaseException):
    """Raised when an organization code is not found or invalid"""
    def __init__(self, org_code: str):
        self.org_code = org_code
        super().__init__(f"Organization code '{org_code}' not found or is invalid")


class BatchFileNotFoundError(ExtractorBaseException):
    """Raised when a batch file doesn't exist"""
    def __init__(self, batch_id: str, org_code: str = None):
        self.batch_id = batch_id
        self.org_code = org_code
        msg = f"Batch file '{batch_id}' not found"
        if org_code:
            msg += f" for organization '{org_code}'"
        super().__init__(msg)


class DownloadFailedError(ExtractorBaseException):
    """Raised when file download fails"""
    def __init__(self, url: str, reason: str = None):
        self.url = url
        self.reason = reason
        msg = f"Failed to download file from '{url}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class StorageError(ExtractorBaseException):
    """Raised when database or filesystem storage operation fails"""
    def __init__(self, operation: str, reason: str = None):
        self.operation = operation
        self.reason = reason
        msg = f"Storage operation '{operation}' failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class RateLimitExceededError(ExtractorBaseException):
    """Raised when API rate limit is exceeded"""
    def __init__(self, retry_after: int = None):
        self.retry_after = retry_after
        msg = "API rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        super().__init__(msg)


class ValidationError(ExtractorBaseException):
    """Raised when input validation fails"""
    def __init__(self, field: str, value: any, reason: str = None):
        self.field = field
        self.value = value
        self.reason = reason
        msg = f"Validation failed for field '{field}' with value '{value}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class ParseError(ExtractorBaseException):
    """Raised when parsing API response fails"""
    def __init__(self, content: str, reason: str = None):
        self.content = content
        self.reason = reason
        msg = "Failed to parse response"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class AuthenticationError(ExtractorBaseException):
    """Raised when authentication with ClassPlus API fails"""
    def __init__(self, reason: str = None):
        self.reason = reason
        msg = "Authentication failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
