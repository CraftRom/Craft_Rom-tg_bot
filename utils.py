import json
import logging
import os

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import CallbackContext, ContextTypes

CHANNELS_FILE = 'channels.json'


def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_channels(channels):
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f, indent=4)


async def find_owner_id(bot, chat_id):
    try:
        administrators = await bot.get_chat_administrators(chat_id)
        for admin in administrators:
            if admin.status == 'creator':
                return admin.user.id
    except Exception as e:
        print(f"Error fetching owner ID: {e}")
    return None


async def is_chat_initialized(chat_id):
    channels = load_channels()
    return any(channel['channel_id'] == str(chat_id) for channel in channels)


async def is_user_admin(update: Update, context: CallbackContext, user_id: int, chat_id: int) -> bool:
    admins = await context.bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True

    hidden_admin_events = context.chat_data.get(chat_id, {}).get('hidden_admin_events', [])
    for event in hidden_admin_events:
        if isinstance(event,
                      ChatMemberUpdated) and event.chat.id == chat_id and event.new_chat_member.user.id == user_id:
            if event.new_chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return True

    return False


class FileInfo:
    def __init__(self, name: str, size: str, last_updated: str, download_link: str):
        self.name = name
        self.size = size
        self.last_updated = last_updated
        self.download_link = download_link


def extract_files_list(url: str) -> List[FileInfo]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        files = []
        for row in soup.select("tr.file"):
            name = row.select_one("span.name").text.strip()
            size = row.select_one("td.opt[headers=files_size_h]").text.strip()
            last_updated_str = row.select_one("td.opt[headers=files_date_h] abbr").get("title")
            last_updated_date = datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S %Z")
            last_updated = last_updated_date.strftime("%m/%d/%Y")
            download_link = row.select_one("a").get("href")
            files.append(FileInfo(name, size, last_updated, download_link))
        return files
    except (requests.RequestException, ValueError, AttributeError) as e:
        logging.error(f"Error while extracting files list from {url}: {e}")
        return []

async def fetch_devices_data() -> Optional[List[Dict[str, Any]]]:
    try:
        response = requests.get('https://raw.githubusercontent.com/craftrom-os/official_devices/master/devices.json')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching devices data: {e}")
        return None

def get_supported_devices(devices_data: List[Dict[str, Any]]) -> List[str]:
    supported_devices = []
    for device in devices_data:
        name = device['name']
        variant_names = device.get('variant_name', [])
        variant_names_str = ", ".join(variant_names) if variant_names else device['codename']
        non_deprecated_versions = [
            version for version in device.get('supported_versions', [])
            if not version.get('deprecated')
        ]
        if non_deprecated_versions:
            supported_devices.append(f" - {name} ({variant_names_str})")
    return supported_devices

def get_device_by_code(devices_data: List[Dict[str, Any]], device_code: str) -> Optional[Dict[str, Any]]:
    return next((d for d in devices_data if device_code in d.get('variant_name', [])), None)

async def send_error_message(update, message: str):
    await update.message.reply_text(f"<b>Error:</b> {message}", parse_mode='HTML')

async def send_message(update, message: str, parse_mode='HTML', disable_web_page_preview=True):
    await update.message.reply_text(message, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)        
