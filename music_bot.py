import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from youtube_dl import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# Telegram Bot Token
TOKEN = "8113371242:AAGazinIis9Ehjy2YZCwP-pWGAh5HhEZMgU"

# PyTgCalls client
pytgcalls = PyTgCalls(client=None)

# Function to handle /play command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = " ".join(context.args)
    if not user_input:
        await update.message.reply_text("Please provide a song name or YouTube link after /play.")
        return

    # Check if the input is a YouTube link
    if "youtube.com" in user_input or "youtu.be" in user_input:
        url = user_input
    else:
        # Search YouTube for the song name
        ydl_opts = {
            "format": "bestaudio/best",
            "default_search": "ytsearch",
            "noplaylist": True,
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{user_input}", download=False)["entries"][0]
            url = info["url"]

    # Join the voice chat and play the audio
    chat_id = update.message.chat_id
    try:
        await pytgcalls.join_group_call(
            chat_id,
            AudioPiped(url),
        )
        await update.message.reply_text(f"Now playing: {user_input}")
    except Exception as e:
        await update.message.reply_text(f"Failed to play audio: {e}")

# Function to handle /skip command
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    try:
        await pytgcalls.leave_group_call(chat_id)
        await update.message.reply_text("Skipped the current song.")
    except Exception as e:
        await update.message.reply_text(f"Failed to skip: {e}")

# Function to handle /stop command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    try:
        await pytgcalls.leave_group_call(chat_id)
        await update.message.reply_text("Stopped playback.")
    except Exception as e:
        await update.message.reply_text(f"Failed to stop: {e}")

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("skip", skip))
    application.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    # Initialize PyTgCalls
    pytgcalls.start()
    main()
    
    

   
