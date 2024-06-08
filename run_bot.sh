#!/bin/bash

LOGFILE="/home/ubuntu/tg_bot/botstart.log"

echo "Starting bot script at $(date)" >> $LOGFILE

# Переконайтеся, що знаходитесь в правильній директорії
cd /home/ubuntu/tg_bot || { echo "Failed to change directory to /home/ubuntu/tg_bot" >> $LOGFILE; exit 1; }

# Встановіть залежності, якщо ще не встановлені
if ! command -v python3 &>/dev/null; then
    echo "Installing Python 3..."
    sudo apt install -y python3
fi

if ! command -v pip &>/dev/null; then
    echo "Installing pip..."
    sudo apt install -y python3-pip
fi

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt >> $LOGFILE 2>&1 || { echo "Failed to install requirements" >> $LOGFILE; exit 1; }

# Запустіть ваш бот
python3 bot_start.py >> $LOGFILE 2>&1 || { echo "Failed to start bot" >> $LOGFILE; exit 1; }

echo "Bot script finished at $(date)" >> $LOGFILE

