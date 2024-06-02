import os
from telegram.ext import Updater, CommandHandler
from commands import start, rom

if __name__ == '__main__':
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('rom', rom, pass_args=True))

    updater.start_polling()
    updater.idle()
