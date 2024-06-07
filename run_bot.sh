#!/bin/bash

# Virtual environment name
VENV_DIR=".venv"

# Function to create a virtual environment
create_venv() {
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
  source $VENV_DIR/bin/activate
}

# Function to activate the virtual environment
activate_venv() {
  echo "Activating virtual environment..."
  if [ -f "$VENV_DIR/bin/activate" ]; then
    source $VENV_DIR/bin/activate
  else
    echo "Error: Failed to activate virtual environment. File $VENV_DIR/bin/activate not found."
    exit 1
  fi
}

# Function to install dependencies
install_dependencies() {
  echo "Installing dependencies..."
  sudo apt install -y python3-pip python3-venv
  python3 -m venv $VENV_DIR
  source $VENV_DIR/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
}

# Function to start the bot with output to terminal and logging to bot.log file
start_bot() {
  echo "Starting the bot..."
  python3 bot_start.py
}

# Check if the virtual environment exists
if [ -d "$VENV_DIR" ]; then
  activate_venv
else
  create_venv
  install_dependencies
fi

# Rename the previous log file to include the date and time of the bot restart
if [ -f "bot.log" ]; then
  mv bot.log "bot_$(date +"%Y%m%d_%H%M%S").log"
fi

# Start the bot and redirect output to terminal and append it to bot.log file
start_bot 2>&1 | tee -a bot.log



