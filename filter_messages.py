from telegram import Update
from telegram.ext import CallbackContext
from utils import load_topic_id


def filter_messages(update: Update, context: CallbackContext):
    proposal_thread_id = load_topic_id()

    # Фільтрування повідомлень за топіком
    if proposal_thread_id and update.message.message_thread_id == proposal_thread_id:
        if "#пропозиція" in update.message.text or "#proposal" in update.message.text or "#suggestion" in update.message.text:
            update.message.reply_text("Your message has been accepted as a suggestion. We will review it.")
        else:
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
