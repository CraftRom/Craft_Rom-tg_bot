import logging
import os
import random

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from commands import start, rom, system_info, clean, set_topic, init
from filter_messages import delete_non_suggestion_messages

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
async def mention_handler(update, context):
    bot_username = context.bot.username
    if bot_username in update.message.text:
        # Відповідь на повідомлення, що бота тегнули
        response = get_random_response()
        update.message.reply_text(response)
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username:
        # Відповідь на повідомлення, що бота тегнули
        response = get_random_response()
        update.message.reply_text(response)


mention_trigger = MessageHandler(filters.TEXT & ~filters.COMMAND, mention_handler)


def main():
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Додавання обробників команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('rom', rom))
    # Додати обробник команди /sysinfo
    application.add_handler(CommandHandler('sysinfo', system_info))
    application.add_handler(CommandHandler('clean', clean))
    application.add_handler(mention_trigger)
    application.add_handler(CommandHandler("set_topic", set_topic))
    application.add_handler(CommandHandler("init", init))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_non_suggestion_messages))

    # Запуск бота
    application.run_polling()
    logger.info("Bot started polling...")


if __name__ == '__main__':
    main()
