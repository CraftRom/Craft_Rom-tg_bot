import os
import logging
from telegram.ext import Updater, CommandHandler
from commands import start, rom

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Обробник повідомлень, що містять згадку про бота
def mention_handler(update, context):
    bot_username = context.bot.username
    if bot_username in update.message.text:
        # Відповідь на повідомлення, що бота тегнули
        update.message.reply_text("Так, ви тегнули мене. Я тут!")


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
