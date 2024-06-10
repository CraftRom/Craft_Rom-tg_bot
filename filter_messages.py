from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from utils import load_channels


async def delete_non_suggestion_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_thread_id = update.message.message_thread_id

    # Load the channels list
    channels = load_channels()

    # Find the chat in the channels list by chat_id
    for channel in channels:
        if channel['channel_id'] == str(chat_id):
            topic_suggestion = channel.get('topic_suggestion')
            if topic_suggestion and str(message_thread_id) == topic_suggestion:
                # Check if the message text does not contain #suggestion
                if '#suggestion' not in update.message.text:
                    try:
                        await context.bot.delete_message(chat_id, update.message.message_id)
                    except Exception as e:
                        print(f"Failed to delete message: {e}")
            break


