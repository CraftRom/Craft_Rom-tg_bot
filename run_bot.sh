#!/bin/bash

# Назва віртуального середовища
VENV_DIR=".venv"

# Функція для створення віртуального середовища
create_venv() {
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
  source $VENV_DIR/bin/activate
}

# Функція для активації віртуального середовища
activate_venv() {
  echo "Activating virtual environment..."
  if [ -f "$VENV_DIR/bin/activate" ]; then
    source $VENV_DIR/bin/activate
  else
    echo "Error: Failed to activate virtual environment. File $VENV_DIR/bin/activate not found."
    exit 1
  fi
}

# Функція для встановлення залежностей
install_dependencies() {
  echo "Installing dependencies..."
  sudo apt install -y python3-pip python3-venv
  python3 -m venv $VENV_DIR
  source $VENV_DIR/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
}

# Запуск бота с выводом на экран и записью логов в файл bot.log
start_bot() {
  echo "Starting the bot..."
  python3 bot_start.py 2>&1 | tee -a bot.log
}


# Перевірка наявності віртуального середовища
if [ -d "$VENV_DIR" ]; then
  activate_venv
else
  create_venv
  install_dependencies
fi

# Запуск бота
start_bot

