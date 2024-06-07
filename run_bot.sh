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
  source $VENV_DIR/bin/activate
}

# Функція для встановлення залежностей
install_dependencies() {
  echo "Installing dependencies..."
  pip install --upgrade pip
  pip install -r requirements.txt
}

# Функція для запуску бота
start_bot() {
  echo "Starting the bot..."
  python bot_start.py
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
