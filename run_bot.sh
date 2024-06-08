#!/bin/bash

# Virtual environment name
VENV_DIR=".venv"

# Function to install dependencies
install_dependencies() {

}

#!/bin/bash

# Переконайтеся, що знаходитесь в правильній директорії
cd /home/ubuntu/tg_bot

# Створіть та активуйте віртуальне середовище
if [ ! -d ".venv" ]; then
  python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

# Встановіть залежності, якщо ще не встановлені
if [ ! -f ".venv/requirements_installed" ]; then
    echo "Installing dependencies..."
    sudo apt install -y python3-pip python3-venv
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .venv/requirements_installed
fi

# Запустіть ваш бот
python3 bot_start.py
