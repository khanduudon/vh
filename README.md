# ClassPlus Course Extractor Bot

A Telegram bot to extract course information from ClassPlus without login access.

## Features

- Extracts course title, description, and other relevant information from ClassPlus URLs
- Responds directly in Telegram with formatted course information
- Easy to use - just send a ClassPlus course URL to the bot

## Setup

1. Create a Telegram bot using [@BotFather](https://t.me/BotFather) and get your bot token
2. Set the `TELEGRAM_BOT_TOKEN` environment variable with your bot token

## Installation

```bash
pip install -r requirements.txt
```

## Running the Bot

```bash
python -m bot.telegram_bot
```

## Usage

1. Start a chat with your bot on Telegram
2. Send a ClassPlus course URL (e.g., https://classplus.example.com/course/12345)
3. The bot will extract and send back the course information

## Testing

```bash
python -m unittest discover tests
```

## License

This project is licensed under the MIT License.