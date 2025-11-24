"""
Telegram Bot for ClassPlus Batch File Retrieval
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.constants import ParseMode

from bot.api import BatchFileAPI
from bot.exceptions import OrgCodeNotFoundError, ValidationError
from bot.utils import format_file_size

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_ORG_CODE, SELECTING_BATCH = range(2)

# Initialize API
api = BatchFileAPI()

# Telegram file size limit (50 MB for bots)
TELEGRAM_FILE_SIZE_LIMIT = 50 * 1024 * 1024


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = f"""
👋 Welcome {user.mention_html()}!

I'm the **ClassPlus Batch File Retrieval Bot**.

I can help you download batch files from ClassPlus by organization code.

📋 **Available Commands:**
/start - Show this welcome message
/help - Get help and usage instructions
/getbatches - Retrieve batches for an org code
/cancel - Cancel current operation

🚀 **Quick Start:**
Use /getbatches to begin!
"""
    await update.message.reply_html(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
📖 **How to Use This Bot**

**Step 1:** Use the /getbatches command

**Step 2:** Enter your organization code (3-20 alphanumeric characters)

**Step 3:** Select which batch files you want to download

**Step 4:** Receive your files!

⚠️ **Important Notes:**
• Organization codes must be 3-20 alphanumeric characters
• Files larger than 50 MB cannot be sent via Telegram
• Downloads are cached for faster retrieval

💡 **Tips:**
• Use /cancel to stop any operation
• The bot remembers downloaded files for faster access
• You can download multiple files from the same org code

❓ **Need Help?**
If you encounter any issues, please check:
1. Your organization code is correct
2. The batch files exist in ClassPlus
3. Your internet connection is stable

🔧 **Commands:**
/start - Welcome message
/help - This help message
/getbatches - Start downloading batches
/cancel - Cancel current operation
"""
    await update.message.reply_text(help_text)


async def get_batches_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the batch retrieval conversation."""
    await update.message.reply_text(
        "📝 Please enter the organization code:\n\n"
        "Example: ABC123\n\n"
        "Use /cancel to abort."
    )
    return WAITING_FOR_ORG_CODE


async def receive_org_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate org code, then fetch batches."""
    org_code = update.message.text.strip().upper()
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"🔍 Fetching batches for organization code: `{org_code}`...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Fetch batches
        result = api.get_batches_by_org_code(org_code)
        
        if not result['success']:
            await processing_msg.edit_text(
                f"❌ Error: {result['message']}\n\n"
                "Please check your organization code and try again.\n"
                "Use /getbatches to try again or /cancel to abort."
            )
            return WAITING_FOR_ORG_CODE
        
        # Store org code in context
        context.user_data['org_code'] = org_code
        context.user_data['batches'] = result['batches']
        
        # Create inline keyboard with batch options
        keyboard = []
        for batch in result['batches'][:20]:  # Limit to 20 batches
            button_text = f"{batch['batch_name']} ({batch['file_size_formatted']})"
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"download_{batch['batch_id']}"
                )
            ])
        
        # Add "Download All" option if there are batches
        if result['batches']:
            keyboard.append([
                InlineKeyboardButton(
                    "📥 Download All Batches",
                    callback_data="download_all"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_text(
            f"✅ Found {result['batch_count']} batches for **{result['org_name']}**\n\n"
            f"Select a batch to download:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SELECTING_BATCH
        
    except Exception as e:
        logger.error(f"Error fetching batches: {e}")
        await processing_msg.edit_text(
            f"❌ An error occurred: {str(e)}\n\n"
            "Please try again later or contact support."
        )
        return ConversationHandler.END


async def download_batch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle batch download button press."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    org_code = context.user_data.get('org_code')
    
    if query.data == "download_all":
        # Download all batches
        await query.edit_message_text(
            "📥 Downloading all batches...\n"
            "This may take a while. Please wait..."
        )
        
        batches = context.user_data.get('batches', [])
        success_count = 0
        failed_count = 0
        
        for batch in batches:
            try:
                result = api.download_batch(batch['batch_id'], org_code)
                
                if result['success']:
                    file_data = result['file_data']
                    
                    # Check file size
                    if len(file_data) > TELEGRAM_FILE_SIZE_LIMIT:
                        await query.message.reply_text(
                            f"⚠️ {result['filename']} is too large "
                            f"({result['file_size_formatted']}) to send via Telegram.\n"
                            f"Maximum size: 50 MB"
                        )
                        failed_count += 1
                        continue
                    
                    # Send file
                    await query.message.reply_document(
                        document=file_data,
                        filename=result['filename'],
                        caption=f"📄 {batch['batch_name']}\n"
                                f"Size: {result['file_size_formatted']}"
                    )
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error downloading batch {batch['batch_id']}: {e}")
                failed_count += 1
        
        await query.message.reply_text(
            f"✅ Download complete!\n\n"
            f"✓ Successfully downloaded: {success_count}\n"
            f"✗ Failed: {failed_count}"
        )
        
        return ConversationHandler.END
    
    else:
        # Download single batch
        batch_id = query.data.replace("download_", "")
        
        await query.edit_message_text(
            f"📥 Downloading batch file...\n"
            f"Please wait..."
        )
        
        try:
            result = api.download_batch(batch_id, org_code)
            
            if not result['success']:
                await query.edit_message_text(
                    f"❌ Download failed: {result['message']}"
                )
                return ConversationHandler.END
            
            file_data = result['file_data']
            
            # Check file size
            if len(file_data) > TELEGRAM_FILE_SIZE_LIMIT:
                await query.edit_message_text(
                    f"⚠️ File is too large ({result['file_size_formatted']}) "
                    f"to send via Telegram.\n"
                    f"Maximum size: 50 MB\n\n"
                    f"Please download it directly from ClassPlus."
                )
                return ConversationHandler.END
            
            # Send file
            await query.message.reply_document(
                document=file_data,
                filename=result['filename'],
                caption=f"📄 {result['filename']}\n"
                        f"Size: {result['file_size_formatted']}\n"
                        f"Type: {result['content_type']}"
            )
            
            await query.edit_message_text(
                "✅ File sent successfully!\n\n"
                "Use /getbatches to download more files."
            )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error downloading batch: {e}")
            await query.edit_message_text(
                f"❌ An error occurred: {str(e)}\n\n"
                "Please try again later."
            )
            return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "❌ Operation cancelled.\n\n"
        "Use /getbatches to start again."
    )
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred while processing your request.\n"
            "Please try again later."
        )


def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set!")
    
    logger.info("Initializing bot...")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('getbatches', get_batches_start)],
        states={
            WAITING_FOR_ORG_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_org_code)
            ],
            SELECTING_BATCH: [
                CallbackQueryHandler(download_batch_callback)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot with robust conflict resolution
    logger.info("Starting bot...")
    try:
        # Run with drop_pending_updates and proper polling settings
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Clear old updates
            close_loop=False,  # Don't close event loop on exit
            stop_signals=None  # Handle signals manually
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
        raise


if __name__ == '__main__':
    main()
