import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Settings - Use environment variables for Cloud Run
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8382908203:AAFcG1-kIoQSgmX7GP8HfUDyOwlI8GZN73k")
TARGET_USER_ID = int(os.environ.get("TARGET_USER_ID", "835851252"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://hotdogbot.fly.dev")  # Set this to your Cloud Run URL
REACTIONS = ["🌭"]  # Hot dog reactions

# Flask app
app = Flask(__name__)

# Telegram bot application
bot_app = Application.builder().token(BOT_TOKEN).build()

class ReactionBot:
    def __init__(self, reactions):
        self.reactions = reactions
        self.current_reaction_index = 0
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages in the group"""
        message = update.message
        
        if not message:
            return
        
        # Logging
        logger.info("=== MESSAGE RECEIVED ===")
        logger.info(f"From: {message.from_user.first_name} (ID: {message.from_user.id})")
        logger.info(f"Chat: {message.chat.title if message.chat.title else 'Private'} (ID: {message.chat.id})")
        logger.info(f"Text: {message.text[:50] if message.text else 'No text'}")
        logger.info("=" * 30)
        
        # Set reaction to ALL messages (removed target user check)
        try:
            # Choose reaction in cycle
            reaction = self.reactions[self.current_reaction_index]
            self.current_reaction_index = (self.current_reaction_index + 1) % len(self.reactions)
            
            # Set reaction
            await message.set_reaction(reaction)
            logger.info(f"[OK] Reaction {reaction} set successfully!")
        except Exception as e:
            logger.error(f"[ERROR] Failed to set reaction: {e}")
            logger.error(f"Error type: {type(e).__name__}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /start"""
        await update.message.reply_text(
            "Bot activated!\n"
            "I will set hot-dogs to messages"
        )
    
    async def get_user_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /myid - shows user ID"""
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "no username"
        first_name = update.message.from_user.first_name
        
        await update.message.reply_text(
            f"Your ID: {user_id}\n"
            f"Name: {first_name}\n"
            f"Username: @{username}"
        )

# Initialize bot
reaction_bot = ReactionBot(REACTIONS)

# Add handlers
bot_app.add_handler(CommandHandler("start", reaction_bot.start_command))
bot_app.add_handler(CommandHandler("myid", reaction_bot.get_user_id_command))
bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, reaction_bot.handle_message))

# Initialize bot application (don't call initialize here)
# bot_app.initialize()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        asyncio.run(bot_app.process_update(update))
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'Error', 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return 'OK', 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook URL - visit this URL after deployment"""
    if not WEBHOOK_URL:
        return 'WEBHOOK_URL not set in environment variables', 400
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    asyncio.run(bot_app.bot.set_webhook(webhook_url))
    logger.info(f"Webhook set to {webhook_url}")
    return f'Webhook set to {webhook_url}', 200

if __name__ == '__main__':
    # For Fly.io and local testing
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
