from telegram import Update
from telegram.ext import CommandHandler, filters, MessageHandler, ContextTypes
from src.telegram.commands import CommandHandlers
from src.db.sqlite_store import SQLiteStore
from src.config import Config
import logging

logger = logging.getLogger(__name__)

async def unauthorized_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers clearly for unauthorized users."""
    await update.message.reply_text("Usuário não autorizado para este bot.")

def register_handlers(application, store: SQLiteStore):
    """Registers all command and message handlers."""
    handlers = CommandHandlers(store)
    
    # Authorized commands
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help))
    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(CommandHandler("ultimas", handlers.ultimas))
    application.add_handler(CommandHandler("pause", handlers.pause))
    application.add_handler(CommandHandler("resume", handlers.resume))
    application.add_handler(CommandHandler("testalert", handlers.testalert))
    
    # Unauthorized feedback
    # We could use a filter for non-authorized users, but simpler for V1 to just handle it inside commands or here.
    # To be more robust, we could add a check at the beginning of each command handler.
    
    # Generic message handler for anything else
    async def echo_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if user_id in Config.TELEGRAM_ALLOWED_USERS:
            await update.message.reply_text("Este bot é focado em alertas de OMs e comandos operacionais. Use /help para ver os comandos.")
        else:
            await unauthorized_feedback(update, context)
            
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo_unsupported))
