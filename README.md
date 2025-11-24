# ClassPlus Batch File Retrieval Bot

A comprehensive Telegram bot to retrieve and download batch files from ClassPlus by organization code. Deployed on Render.com with MongoDB Atlas for scalable file storage.

## 🤖 Telegram Bot Features

- **Easy to Use**: Simple conversation-based interface
- **Batch Retrieval**: Get all batches for any organization code
- **File Downloads**: Download batch files directly in Telegram
- **Smart Caching**: Fast retrieval with multi-tier caching
- **Progress Tracking**: Real-time download progress updates
- **Error Handling**: Clear error messages and help text

## 🌟 System Features

- **Batch File Retrieval**: Retrieve all batch files associated with an organization code
- **Actual File Downloads**: Returns complete file content, not just metadata
- **Multi-tier Caching**: Efficient caching with memory, filesystem, and database layers
- **Automatic Retry Logic**: Handles network failures with exponential backoff
- **Rate Limiting**: Prevents API throttling with configurable rate limits
- **GridFS Storage**: Scalable file storage using MongoDB GridFS
- **Comprehensive API**: Clean, well-documented API for all operations
- **Error Handling**: Robust error handling with detailed error messages

## Installation

### For Deployment on Render.com

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

**Quick Start:**
1. Create a Telegram bot with [@BotFather](https://t.me/botfather)
2. Set up MongoDB Atlas (free tier)
3. Push code to GitHub
4. Deploy to Render.com
5. Configure environment variables

### For Local Development

#### Prerequisites

- Python 3.7+
- MongoDB 4.0+ (or MongoDB Atlas)
- Telegram Bot Token

#### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your credentials
```

4. Start MongoDB (if running locally):
```bash
mongod
```

5. Run the bot:
```bash
python telegram_bot.py
```

## 🤖 Using the Telegram Bot

### Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Detailed help and usage instructions
- `/getbatches` - Start batch retrieval process
- `/cancel` - Cancel current operation

### How to Use

1. **Start the bot**: Send `/start` to your bot
2. **Get batches**: Send `/getbatches`
3. **Enter org code**: Type your organization code (e.g., `ABC123`)
4. **Select files**: Choose which batch files to download
5. **Receive files**: Files are sent directly in Telegram

### Example Workflow

```
You: /getbatches
Bot: 📝 Please enter the organization code:

You: ABC123
Bot: ✅ Found 5 batches for Example Org
     [Select a batch to download]
     
You: [Click on a batch]
Bot: 📥 Downloading batch file...
     ✅ File sent successfully!
     📄 batch_001.pdf (1.2 MB)
```

## 💻 Programmatic Usage (API)

### Quick Start

```python
from bot.api import BatchFileAPI

# Initialize API
api = BatchFileAPI()

# Get all batches for an organization
result = api.get_batches_by_org_code("ABC123")

if result['success']:
    print(f"Found {result['batch_count']} batches")
    for batch in result['batches']:
        print(f"- {batch['batch_name']}: {batch['file_size_formatted']}")
```

### Download Batch Files

```python
# Download a specific batch file
result = api.download_batch("batch_001", "ABC123")

if result['success']:
    # Save file to disk
    with open(result['filename'], 'wb') as f:
        f.write(result['file_data'])
    print(f"Downloaded {result['filename']}")
```

### Sync All Batches

```python
# Download all batch files for an organization
result = api.sync_org_batches("ABC123")

if result['success']:
    print(f"Downloaded {result['downloaded_files']}/{result['total_files']} files")
    print(f"Total size: {result['total_bytes_formatted']}")
```

### Legacy Course Extraction

```python
from bot.extractor import ClassPlusExtractor

extractor = ClassPlusExtractor(base_url="https://classplus.example.com")
course_info = extractor.fetch_course_info(course_id="12345")
print(course_info)
```

## API Documentation

For detailed API documentation, see [BATCH_API.md](BATCH_API.md).

## System Architecture

The system consists of several layers:

1. **API Layer** (`api.py`): Clean interface for batch operations
2. **Service Layer** (`batch_service.py`): Core business logic
3. **Data Layer** (`database.py`): MongoDB and GridFS operations
4. **Extractor Layer** (`extractor.py`): ClassPlus API integration
5. **Models** (`models.py`): Data models and schemas
6. **Utilities** (`utils.py`): Helper functions

### Data Flow

```
User Request → API → Batch Service → Extractor → ClassPlus API
                ↓                          ↓
            Database ← GridFS Storage ← File Download
                ↓
          File Cache
```

## Configuration

All configuration is done via environment variables. See [BATCH_API.md](BATCH_API.md#configuration) for details.

## Testing

Run unit tests:
```bash
python -m unittest discover tests
```

Run specific test file:
```bash
python -m unittest tests.test_batch_service
```

## Examples

See `example_usage.py` for comprehensive examples:
```bash
python example_usage.py
```

## Error Handling

The system provides detailed error messages for common issues:

- `OrgCodeNotFoundError`: Invalid organization code
- `BatchFileNotFoundError`: Batch file doesn't exist
- `DownloadFailedError`: File download failed
- `ValidationError`: Input validation failed
- `StorageError`: Database/filesystem error
- `RateLimitExceededError`: API rate limit exceeded

## Performance

- **Caching**: Multi-tier caching reduces API calls and improves response time
- **Rate Limiting**: Configurable rate limiting prevents API throttling
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **GridFS**: Efficient storage and retrieval of large files

## 🚀 Deployment

### Render.com (Recommended)

This bot is designed to be deployed on Render.com with MongoDB Atlas.

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions.**

**Quick Deploy:**
1. Create Telegram bot with [@BotFather](https://t.me/botfather)
2. Set up free MongoDB Atlas cluster
3. Push code to GitHub
4. Connect GitHub to Render.com
5. Configure environment variables
6. Deploy!

**Environment Variables Required:**
- `BOT_TOKEN` - Your Telegram bot token
- `MONGODB_URI` - MongoDB Atlas connection string
- `DATABASE_NAME` - Database name (default: `classplus_extractor`)

### Other Platforms

The bot can also be deployed on:
- **Heroku**: Use `Procfile` (included)
- **Railway**: Similar to Render.com
- **VPS**: Run with `python telegram_bot.py`
- **Docker**: Create Dockerfile (not included)

## 📁 Project Structure

```
Extractor/
├── bot/
│   ├── __init__.py
│   ├── api.py              # API layer
│   ├── batch_service.py    # Service layer
│   ├── config.py           # Configuration
│   ├── database.py         # Database layer
│   ├── exceptions.py       # Custom exceptions
│   ├── extractor.py        # ClassPlus API integration
│   ├── logger.py           # Logging configuration
│   ├── models.py           # Data models
│   └── utils.py            # Utility functions
├── tests/
│   ├── test_batch_service.py
│   └── test_extractor.py
├── telegram_bot.py         # Telegram bot main file
├── example_usage.py        # API usage examples
├── requirements.txt        # Python dependencies
├── render.yaml            # Render.com configuration
├── Procfile               # Process file for deployment
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── README.md              # This file
├── DEPLOYMENT.md          # Deployment guide
├── BATCH_API.md           # API documentation
└── LICENSE                # MIT License

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
