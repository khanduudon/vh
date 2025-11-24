"""
Setup script to create .env file with your MongoDB credentials
Run this script to quickly set up your local environment
"""

import os

def create_env_file():
    """Create .env file with MongoDB credentials"""
    
    print("=" * 60)
    print("ClassPlus Batch Bot - Environment Setup")
    print("=" * 60)
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get bot token from user
    print("Your Telegram Bot Token is already configured!")
    print("Bot Token: 8266651898:AAFTdgzKg9Cse8Wzw8aoH6XuDJ7TZ2-RefU")
    print()
    
    use_configured = input("Use this token? (y/n, default: y): ").strip().lower()
    
    if use_configured == 'n':
        bot_token = input("Enter your Telegram Bot Token: ").strip()
        if not bot_token:
            print("Error: Bot token cannot be empty!")
            return
    else:
        bot_token = "8508365196:AAFQF5mD5RFEq1YBYxztSgPIjt0clxUhMzE"
    
    # MongoDB is already configured
    mongodb_uri = "mongodb+srv://nk9582235_db_user:TVM1VuULifESdFb9@cluster0.gsewrqr.mongodb.net/?appName=Cluster0"
    database_name = "classplus_extractor"
    
    print()
    print("MongoDB Atlas is already configured!")
    print(f"Database: {database_name}")
    print()
    
    # Create .env content
    env_content = f"""# Environment Variables for Local Development
# DO NOT COMMIT THIS FILE TO GITHUB!

# Telegram Bot Configuration
BOT_TOKEN={bot_token}

# MongoDB Configuration (MongoDB Atlas)
MONGODB_URI={mongodb_uri}
DATABASE_NAME={database_name}

# ClassPlus API Configuration
CLASSPLUS_BASE_URL=https://api.classplusapp.com
API_TIMEOUT=30
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60

# File Storage
MAX_FILE_SIZE=104857600
CACHE_ENABLED=True
CACHE_DIR=./cache/batch_files
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=extractor.log

# Parallel Downloads
MAX_CONCURRENT_DOWNLOADS=5
DOWNLOAD_CHUNK_SIZE=8192

# Security
VALIDATE_SSL=True
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! .env file created successfully!")
        print("=" * 60)
        print()
        print("Configuration:")
        print(f"  ✓ Bot Token: {bot_token[:20]}...")
        print(f"  ✓ MongoDB: cluster0.akuzmvw.mongodb.net")
        print(f"  ✓ Database: {database_name}")
        print()
        print("Next Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the bot: python telegram_bot.py")
        print("  3. Test in Telegram!")
        print()
        print("⚠️  IMPORTANT: Never commit .env file to GitHub!")
        print("   (It's already in .gitignore)")
        print()
        
    except Exception as e:
        print(f"Error creating .env file: {e}")


if __name__ == "__main__":
    create_env_file()

