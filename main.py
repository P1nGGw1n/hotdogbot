import asyncio, sys
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# Настройки
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BOT_TOKEN = "8382908203:AAFcG1-kIoQSgmX7GP8HfUDyOwlI8GZN73k"
TARGET_USER_ID = 835851252  # ID пользователя, которому ставить реакции
REACTIONS = ["🌭"]  # Список возможных реакций

class ReactionBot:
    def __init__(self, token, target_user_id, reactions):
        self.token = token
        self.target_user_id = target_user_id
        self.reactions = reactions
        self.current_reaction_index = 0
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает все сообщения в группе"""
        message = update.message
        
        # LOGGING - see all messages
        print(f"\n=== MESSAGE RECEIVED ===")
        print(f"From: {message.from_user.first_name} (ID: {message.from_user.id})")
        print(f"Chat: {message.chat.title if message.chat.title else 'Private'} (ID: {message.chat.id})")
        print(f"Text: {message.text[:50] if message.text else 'No text'}")
        print("=" * 30)
        
        # Check if message is from target user
        try:
            # Choose reaction in cycle
            reaction = self.reactions[self.current_reaction_index]
            self.current_reaction_index = (self.current_reaction_index + 1) % len(self.reactions)
                
            # Set reaction
            await message.set_reaction(reaction)
            print(f"[OK] Reaction {reaction} set successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to set reaction: {e}")
            print(f"Error type: {type(e).__name__}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /start"""
        await update.message.reply_text(
            f"Bot activated!\n"
            f"I will set hot-dogs to messages"
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
    
    def run(self):
        """Запускает бота"""
        app = Application.builder().token(self.token).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("myid", self.get_user_id_command))
        app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_message))
        
        print("Bot started! Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Создаём и запускаем бота
    bot = ReactionBot(
        token=BOT_TOKEN,
        target_user_id=TARGET_USER_ID,
        reactions=REACTIONS
    )
    bot.run()
