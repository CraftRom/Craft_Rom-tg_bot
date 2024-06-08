#!/bin/bash

LOGFILE="/home/ubuntu/tg_bot/botstart.log"

echo "Starting bot script at $(date)" >> $LOGFILE

# Переконайтеся, що знаходитесь в правильній директорії
cd /home/ubuntu/tg_bot || { echo "Failed to change directory to /home/ubuntu/tg_bot" >> $LOGFILE; exit 1; }

# Створіть та активуйте віртуальне середовище
if [ ! -d ".venv" ]; then
    python3 -m venv .venv || { echo "Failed to create virtual environment" >> $LOGFILE; exit 1; }
fi

source .venv/bin/activate || { echo "Failed to activate virtual environment" >> $LOGFILE; exit 1; }

# Встановіть залежності, якщо ще не встановлені
if [ ! -f ".venv/requirements_installed" ]; then
    echo "Installing dependencies..."
    sudo apt install -y python3-pip python3-venv
    pip install --upgrade pip
    pip install -r requirements.txt >> $LOGFILE 2>&1 || { echo "Failed to install requirements" >> $LOGFILE; exit 1; }
    touch .venv/requirements_installed
fi

# Запустіть ваш бот
python3 bot_start.py >> $LOGFILE 2>&1 || { echo "Failed to start bot" >> $LOGFILE; exit 1; }

echo "Bot script finished at $(date)" >> $LOGFILE

