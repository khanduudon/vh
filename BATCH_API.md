# Batch File API Documentation

## Overview

The Batch File API provides a simple interface to retrieve all batch files associated with an organization code from ClassPlus. The system returns actual batch files (not just metadata) and stores them for efficient retrieval.

## Quick Start

```python
from bot.api import BatchFileAPI

# Initialize API
api = BatchFileAPI()

# Get all batches for an org code
result = api.get_batches_by_org_code("ABC123")

# Download a specific batch file
file_result = api.download_batch("batch_001", "ABC123")

# Sync all batches (download all files)
sync_result = api.sync_org_batches("ABC123")
```

## API Reference

### BatchFileAPI Class

Main API interface for batch file operations.

#### `get_batches_by_org_code(org_code, force_refresh=False)`

Retrieve all batch files for an organization code.

**Parameters:**
- `org_code` (str): Organization code (3-20 alphanumeric characters)
- `force_refresh` (bool, optional): If True, fetch from API even if cached. Default: False

**Returns:**
Dictionary with the following structure:
```python
{
    "success": bool,
    "message": str,
    "org_code": str,
    "org_name": str,
    "batch_count": int,
    "batches": [
        {
            "batch_id": str,
            "batch_name": str,
            "filename": str,
            "file_size": int,  # bytes
            "file_size_formatted": str,  # e.g., "1.5 MB"
            "content_type": str,  # MIME type
            "created_at": str,  # ISO 8601 format
            "downloaded": bool,
            "downloaded_at": str  # ISO 8601 format or null
        },
        ...
    ]
}
```

**Example:**
```python
result = api.get_batches_by_org_code("ABC123")
if result['success']:
    print(f"Found {result['batch_count']} batches")
    for batch in result['batches']:
        print(f"- {batch['batch_name']}: {batch['file_size_formatted']}")
```

---

#### `download_batch(batch_id, org_code)`

Download a specific batch file and return the file content.

**Parameters:**
- `batch_id` (str): Batch file ID
- `org_code` (str): Organization code

**Returns:**
Dictionary with the following structure:
```python
{
    "success": bool,
    "message": str,
    "batch_id": str,
    "filename": str,
    "file_size": int,
    "file_size_formatted": str,
    "content_type": str,
    "file_data": bytes  # Actual file content
}
```

**Example:**
```python
result = api.download_batch("batch_001", "ABC123")
if result['success']:
    # Save file to disk
    with open(result['filename'], 'wb') as f:
        f.write(result['file_data'])
    print(f"Downloaded {result['filename']} ({result['file_size_formatted']})")
```

---

#### `sync_org_batches(org_code, force_refresh=False)`

Synchronize all batch files for an organization (fetch metadata and download all files).

**Parameters:**
- `org_code` (str): Organization code
- `force_refresh` (bool, optional): If True, re-download even if files exist. Default: False

**Returns:**
Dictionary with the following structure:
```python
{
    "success": bool,
    "message": str,
    "org_code": str,
    "total_files": int,
    "downloaded_files": int,
    "failed_files": int,
    "total_bytes": int,
    "total_bytes_formatted": str,
    "progress_percentage": float,
    "duration_seconds": float
}
```

**Example:**
```python
result = api.sync_org_batches("ABC123")
if result['success']:
    print(f"Downloaded {result['downloaded_files']}/{result['total_files']} files")
    print(f"Total size: {result['total_bytes_formatted']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
```

---

#### `get_batch_info(batch_id)`

Get detailed information about a specific batch file.

**Parameters:**
- `batch_id` (str): Batch file ID

**Returns:**
Dictionary with the following structure:
```python
{
    "success": bool,
    "message": str,
    "batch": {
        "batch_id": str,
        "org_code": str,
        "batch_name": str,
        "filename": str,
        "file_size": int,
        "file_size_formatted": str,
        "content_type": str,
        "created_at": str,
        "downloaded": bool,
        "downloaded_at": str,
        "metadata": dict  # Additional batch metadata
    }
}
```

**Example:**
```python
result = api.get_batch_info("batch_001")
if result['success']:
    batch = result['batch']
    print(f"Batch: {batch['batch_name']}")
    print(f"Size: {batch['file_size_formatted']}")
    print(f"Downloaded: {batch['downloaded']}")
```

---

## Error Handling

All API methods return a dictionary with a `success` field. If `success` is `False`, the response will include an `errors` list with error details.

**Error Response Structure:**
```python
{
    "success": False,
    "message": "Error description",
    "errors": [
        {
            "type": "ErrorType",
            "message": "Detailed error message"
        }
    ]
}
```

**Common Error Types:**
- `OrgCodeNotFoundError`: Invalid or non-existent organization code
- `BatchFileNotFoundError`: Batch file doesn't exist
- `DownloadFailedError`: File download failed
- `ValidationError`: Input validation failed
- `StorageError`: Database or filesystem error
- `RateLimitExceededError`: API rate limit exceeded

**Example Error Handling:**
```python
result = api.get_batches_by_org_code("INVALID")
if not result['success']:
    print(f"Error: {result['message']}")
    for error in result.get('errors', []):
        print(f"  - {error['type']}: {error['message']}")
```

---

## Configuration

The system can be configured using environment variables:

### Database Configuration
- `MONGODB_URI`: MongoDB connection URI (default: `mongodb://localhost:27017/`)
- `DATABASE_NAME`: Database name (default: `classplus_extractor`)

### ClassPlus API Configuration
- `CLASSPLUS_BASE_URL`: ClassPlus API base URL (default: `https://api.classplusapp.com`)
- `API_TIMEOUT`: Request timeout in seconds (default: `30`)
- `MAX_RETRIES`: Maximum retry attempts (default: `3`)
- `RETRY_BACKOFF_FACTOR`: Exponential backoff factor (default: `2.0`)

### Rate Limiting
- `RATE_LIMIT_REQUESTS`: Requests per minute (default: `10`)
- `RATE_LIMIT_PERIOD`: Rate limit period in seconds (default: `60`)

### File Storage
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: `104857600` = 100 MB)
- `CACHE_ENABLED`: Enable file caching (default: `True`)
- `CACHE_DIR`: Cache directory path (default: `./cache/batch_files`)
- `CACHE_TTL`: Cache time-to-live in seconds (default: `3600` = 1 hour)

### Logging
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_FILE`: Log file path (default: `extractor.log`)

**Example Configuration:**
```bash
# .env file
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=my_database
CLASSPLUS_BASE_URL=https://api.classplusapp.com
CACHE_ENABLED=True
CACHE_DIR=./cache
LOG_LEVEL=DEBUG
```

---

## Advanced Usage

### Using Custom Database and Extractor

```python
from bot.api import BatchFileAPI
from bot.database import Database
from bot.extractor import ClassPlusExtractor
from bot.batch_service import BatchService

# Create custom instances
db = Database(uri="mongodb://custom-host:27017/", db_name="custom_db")
extractor = ClassPlusExtractor(base_url="https://custom-api.example.com")
service = BatchService(db=db, extractor=extractor)
api = BatchFileAPI(batch_service=service)

# Use API as normal
result = api.get_batches_by_org_code("ABC123")
```

### Batch Processing Multiple Org Codes

```python
from bot.api import BatchFileAPI

api = BatchFileAPI()
org_codes = ["ABC123", "DEF456", "GHI789"]

for org_code in org_codes:
    print(f"Processing {org_code}...")
    result = api.sync_org_batches(org_code)
    
    if result['success']:
        print(f"  ✓ Downloaded {result['downloaded_files']} files")
    else:
        print(f"  ✗ Error: {result['message']}")
```

### Direct File Access from Storage

```python
from bot.batch_service import BatchService

service = BatchService()

# Get file from storage (cache or GridFS)
file_data = service.get_batch_file_from_storage("batch_001")

if file_data:
    with open("output.pdf", "wb") as f:
        f.write(file_data)
```

---

## Performance Considerations

1. **Caching**: The system uses a multi-tier caching strategy:
   - Memory cache (fastest)
   - Filesystem cache (fast)
   - GridFS database (persistent)

2. **Rate Limiting**: API calls are rate-limited to prevent overwhelming the ClassPlus API. Configure `RATE_LIMIT_REQUESTS` based on your API limits.

3. **Parallel Downloads**: The `sync_org_batches` method downloads files sequentially. For large organizations, consider implementing parallel downloads.

4. **Database Indexing**: The system automatically creates indexes on frequently queried fields for optimal performance.

---

## Best Practices

1. **Always check `success` field** before accessing response data
2. **Use `force_refresh=False`** (default) to leverage caching
3. **Handle errors gracefully** with try-except blocks
4. **Configure appropriate rate limits** to avoid API throttling
5. **Monitor log files** for debugging and performance analysis
6. **Use environment variables** for configuration in production

---

## Examples

See `example_usage.py` for comprehensive examples of all API features.

---

## Support

For issues or questions, please refer to the main README.md or contact the development team.
