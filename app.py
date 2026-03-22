"""
author : @akash
app.py

purpose:
1. Main entry point for the Telegram bot.
2. Handles user interactions, commands, and message processing.
3. Integrates with the RAG logic to provide intelligent responses based on user queries and retrieved context.
4. Manages conversation history and ensures efficient communication with the user while maintaining a responsive experience.
5. Implements error handling to provide feedback to the user in case of issues and logs errors for debugging.
"""

import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from rag import get_llm_response, user_history  
from config import TELEGRAM_TOKEN, user_history

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initializes the bot and greets the user."""
    await update.message.reply_text("Hi! I'm your Telecom Assistant. ###\nAsk me anything or use /ask.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays usage instructions."""
    await update.message.reply_text(
        "Commands:\n"
        "/ask <query> — Ask a question\n"
        "/clear — Reset chat history\n"
        "/help — Show this message"
    )

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears history to maintain efficiency and privacy."""
    user_id = update.message.from_user.id
    if user_id in user_history:
        user_history[user_id] = []
        await update.message.reply_text("🧹 History cleared!")
    else:
        await update.message.reply_text("History is already empty.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes queries and maintains history awareness."""
    user_id = update.message.from_user.id
    # Get query from /ask args or direct text
    user_query = " ".join(context.args) if context.args else update.message.text
    
    if not user_query or user_query.strip() == "":
        await update.message.reply_text("Please provide a question. Example: /ask how do I activate my SIM?")
        return

    status_message = await update.message.reply_text("### Thinking...")
    
    try:
        # 1. Fetch response from RAG
        answer = get_llm_response(user_id, user_query)
        
        try:
            # 2. Try sending with Markdown (for bold sources)
            await update.message.reply_text(answer, parse_mode='Markdown')
        except Exception:
            # 3. Fallback: If Markdown fails (due to stray characters), send as plain text
            await update.message.reply_text(answer)
            
        # Clean up the status message
        await status_message.delete()
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"Oops! I ran into an issue. Try again or use /clear.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_history))
    app.add_handler(CommandHandler("ask", handle_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("### Bot is running...")
    app.run_polling()