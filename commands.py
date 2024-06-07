import logging
import requests
import os
from telegram import Update
from telegram.ext import CallbackContext
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'  # Файл, в который будут записываться логи
)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        '<b>Welcome! This is your bot, ready to assist you.</b>\n\n'
        '<b>Description:</b>\n'
        'This bot provides information about supported devices for CRAFT ROM, including the latest available versions and download links.\n\n'
        '<b>Available Commands:</b>\n'
        '<code>/start</code> - Display this welcome message and list of commands.\n'
        '<code>/rom [device_code]</code> - Get information about the specified device code.\n'
        '<code>/rom</code> - Get a list of all supported device codes.\n'
        'Example: <code>/rom onclite</code>',
        parse_mode='HTML'
    )
    logging.info("User requested /start command.")


class FileInfo:
    def __init__(self, name: str, size: str, last_updated: str, download_link: str):
        self.name = name
        self.size = size
        self.last_updated = last_updated
        self.download_link = download_link


def extract_files_list(url: str) -> List[FileInfo]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx HTTP status codes
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


def rom(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        try:
            response = requests.get(
                'https://raw.githubusercontent.com/craftrom-os/official_devices/master/devices.json')
            response.raise_for_status()  # Raise an exception for 4xx or 5xx HTTP status codes
            devices_data = response.json()
            if not devices_data:
                update.message.reply_text("Device code list is empty or not found.")
            else:
                device_codes = [device['codename'] for device in devices_data]
                device_codes_str = ", ".join(device_codes)
                update.message.reply_text(
                    '<b>Please specify the device code.</b>\n'
                    'Example: <code>/rom onclite</code>\n'
                    'You can also use <code>/rom</code> to get a list of supported devices.\n\n'
                    '<b>List of supported device codes:</b>\n' + device_codes_str,
                    parse_mode='HTML'
                )
        except requests.RequestException as e:
            update.message.reply_text(f"<b>Failed to fetch device codes:</b> {e}", parse_mode='HTML')
            logging.error(f"Failed to fetch device codes: {e}")
        return

    device_code = context.args[0]

    try:
        response = requests.get('https://raw.githubusercontent.com/craftrom-os/official_devices/master/devices.json')
        response.raise_for_status()
        devices_data = response.json()
    except requests.RequestException as e:
        update.message.reply_text(f"<b>Error:</b> {e}", parse_mode='HTML')
        logging.error(f"Error fetching devices data: {e}")
        return

    device_found = False
    for device in devices_data:
        if device.get('codename') == device_code:
            device_found = True
            name = device.get('name')
            brand = device.get('brand')

            supported_versions = device.get('supported_versions', [])
            latest_versions = supported_versions[-2:] if len(supported_versions) >= 2 else supported_versions

            versions_text_list = []
            for version in latest_versions:
                version_code = version.get('version_code')
                sf_url = f"https://sourceforge.net/projects/craftrom/files/{device_code}/{version_code}/"

                try:
                    files_list = extract_files_list(sf_url)
                    if files_list:
                        versions_text_list.append(f'<b>Version:</b> {version_code}')
                        versions_text_list.append(
                            f'<i>Date:</i> {files_list[0].last_updated}\n'
                            f'<i>Download:</i> <a href="{files_list[0].download_link}">{files_list[0].name}</a> ({files_list[0].size})')
                    else:
                        versions_text_list.append(f'<b>Version:</b> {version_code} (Not available)')
                except requests.RequestException as e:
                    versions_text_list.append(f'<b>Version:</b> {version_code} (Error checking availability)')
                    logging.error(f"Error checking availability for version {version_code}: {e}")

            versions_text = "\n".join(versions_text_list)

            message = (
                f"#{device_code} #rom\n"
                f"<b>{brand} | {name}</b>\n\n"
                f"<b>Device codename:</b> {device_code}\n"
                f"{versions_text}\n\n"
                f"<i>Discuss device's, feature's, or just chat about everything.</i>\n"
                f'<a href="https://discord.gg/vErZGrSyqD">DISCORD CRAFTROM</a> | '
                f'<a href="http://t.me/craftrom">CHAT CRAFTROM</a> | '
                f'<a href="http://t.me/craftrom_news">NEWS</a>'
            )
            update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
            logging.info(f"Device info sent for device code {device_code}.")
            break

    if not device_found:
        update.message.reply_text(f"<b>Device code {device_code} not found.</b>", parse_mode='HTML')
        logging.warning(f"Device code {device_code} not found.")

