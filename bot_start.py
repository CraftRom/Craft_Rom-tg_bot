import os
import random
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from commands import start, rom

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Варіанти відповідей
responses = [
    "Yes, you tagged me. I'm here!",
    "Hello! I'm here, ready to assist you.",
    "You called? I'm ready to help.",
    "Here I am! What can I do for you?",
    "Hi! I'm here, ready to answer your questions."
]


# Функція для випадкового вибору відповіді
def get_random_response():
    # Перемішуємо список відповідей
    random.shuffle(responses)
    # Повертаємо перший елемент списку
    return responses[0]


# Обробник повідомлень, що містять згадку про бота
def mention_handler(update, context):
    bot_username = context.bot.username
    if bot_username in update.message.text:
        # Відповідь на повідомлення, що бота тегнули
        response = get_random_response()
        update.message.reply_text(response)
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username:
        # Відповідь на повідомлення, що бота тегнули
        response = get_random_response()
        update.message.reply_text(response)


mention_trigger = MessageHandler(Filters.text & (~Filters.command), mention_handler)


def main():
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # Додавання обробників команд
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('rom', rom, pass_args=True))
    dispatcher.add_handler(mention_trigger)
    # Запуск бота
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()


if __name__ == '__main__':
    main()
