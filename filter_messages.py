import logging
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from utils import load_channels

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'  # Файл, в который будут записываться логи
)

logger = logging.getLogger(__name__)


async def delete_non_suggestion_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_thread_id = update.message.message_thread_id

    logger.info(f"Checking message {update.message.message_id} in thread {message_thread_id}")

    # Load the channels list
    channels = await load_channels()

    # Find the chat in the channels list by chat_id
    for channel in channels:
        if channel['channel_id'] == str(chat_id):
            topic_suggestion = channel.get('topic_suggestion')
            if topic_suggestion and str(message_thread_id) == topic_suggestion:
                logger.info(f"Message {update.message.message_id} matched topic_suggestion {topic_suggestion}")
                # Check if the message text does not contain #suggestion
                if '#suggestion' not in update.message.text:
                    try:
                        await context.bot.delete_message(chat_id, update.message.message_id)
                        logger.info(f"Deleted message {update.message.message_id} in thread {message_thread_id}")
                    except Exception as e:
                        logger.error(f"Failed to delete message {update.message.message_id}: {e}")
            break


