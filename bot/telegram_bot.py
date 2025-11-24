import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from bot.extractor import ClassPlusExtractor

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Store user sessions
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm the ClassPlus Course Extractor Bot.\n"
        "Send me a ClassPlus course URL and I'll extract the course information for you.\n"
        "Example: https://classplus.example.com/course/12345"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Send me a ClassPlus course URL and I'll extract the course information for you.\n"
        "Example: https://classplus.example.com/course/12345"
    )

async def extract_course_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extract course information from the provided URL."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Simple URL validation
    if "classplus" not in message_text.lower():
        await update.message.reply_text("Please send a valid ClassPlus course URL.")
        return
    
    try:
        # Extract base URL and course ID from the message
        # This is a simplified approach - you might want to improve URL parsing
        parts = message_text.split("/")
        if len(parts) < 5:
            await update.message.reply_text("Invalid URL format. Please send a complete ClassPlus course URL.")
            return
            
        base_url = "/".join(parts[:3])  # https://domain.com
        course_id = parts[-1]  # Last part should be the course ID
        
        # Create extractor instance
        extractor = ClassPlusExtractor(base_url=base_url)
        
        # Fetch course information
        course_info = extractor.fetch_course_info(course_id)
        
        if course_info:
            # Format the response
            response = f"*Course Title:* {course_info.get('title', 'N/A')}\n\n"
            response += f"*Description:*\n{course_info.get('description', 'N/A')}\n\n"
            
            # Add any additional fields
            for key, value in course_info.items():
                if key not in ['title', 'description']:
                    response += f"*{key.title()}:* {value}\n"
                    
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("Sorry, I couldn't extract information for this course.")
            
    except Exception as e:
        logger.error(f"Error extracting course info: {str(e)}")
        await update.message.reply_text("An error occurred while extracting course information. Please try again.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text("Sorry, I didn't understand that command. Use /help for assistance.")

def main():
    """Start the bot."""
    # Get token from environment variable or replace with your bot token
    import os
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("Please set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, extract_course_info))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()