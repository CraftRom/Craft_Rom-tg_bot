import logging
from datetime import datetime
from typing import List
import platform
import requests
from bs4 import BeautifulSoup
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import CallbackContext
import psutil
import time

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
            maintainers = device.get('maintainers', 'No maintainers')

            supported_versions = device.get('supported_versions', [])
            latest_versions = supported_versions[-2:] if len(supported_versions) >= 2 else supported_versions

            versions_text_list = []
            for version in latest_versions:
                version_code = version.get('version_code')
                sf_url = f"https://sourceforge.net/projects/craftrom/files/{device_code}/{version_code}/"

                # Check for special version codes
                if version_code == "thrall":
                    version_code = "thrall (Android 13)"
                elif version_code == "uther":
                    version_code = "uther (Android 14)"

                stable = version.get('stable')
                deprecated = version.get('deprecated')
                if stable:
                    if deprecated:
                        version_status = "Stable (Deprecated)"
                    else:
                        version_status = "Stable"
                else:
                    if deprecated:
                        version_status = "Unstable (Deprecated)"
                    else:
                        version_status = "Unstable"

                try:
                    files_list = extract_files_list(sf_url)
                    if files_list:
                        versions_text_list.append(f'▪️<b>Version:</b> {version_code}')
                        versions_text_list.append(
                            f'\n • <i>Date:</i> {files_list[0].last_updated}\n'
                            f' • <i>Status:</i> {version_status}\n'
                            f' • <i>Download:</i> <a href="{files_list[0].download_link}">{files_list[0].name}</a> ({files_list[0].size})')
                    else:
                        versions_text_list.append(f'▪️<b>Version:</b> {version_code} (Not available)')
                except requests.RequestException as e:
                    versions_text_list.append(f'▪️<b>Version:</b> {version_code} (Error checking availability)')
                    logging.error(f"Error checking availability for version {version_code}: {e}")

            versions_text = "\n".join(versions_text_list)

            message = (
                f"#{device_code} #rom\n"
                f"<b>{brand} | {name}</b>\n\n"
                f'Device information: <a href="https://craft-rom.pp.ua/devices/{device_code}/">here</a>\n\n'
                f"▪️<b>Device codename:</b> {device_code}\n"
                f"▪️<b>Maintainer:</b> {maintainers}\n"
                f"{versions_text}\n\n\n"
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


def system_info(update: Update, context: CallbackContext) -> None:
    # Check if the user is an admin
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if the user is an admin
    is_admin = False
    admins = context.bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            is_admin = True
            break

    # Check if the user is a hidden admin
    is_hidden_admin = False
    for event in context.dispatcher.chat_data.get(chat_id, {}).get('hidden_admin_events', []):
        if isinstance(event,
                      ChatMemberUpdated) and event.chat.id == chat_id and event.new_chat_member.user.id == user_id:
            is_hidden_admin = event.new_chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
            break

    # If the user is neither an admin nor a hidden admin, deny access
    if not is_admin and not is_hidden_admin:
        update.message.reply_text("You must be an admin to use this command.")
        return

    # Get system uptime
    uptime = time.time() - psutil.boot_time()
    uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime))

    # Get CPU and RAM usage
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent

    # Get memory information
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total
    available_memory = memory_info.available

    # Get OS and kernel information
    os_name = platform.system()
    os_version = platform.version()
    kernel_version = platform.release()

    # Read bot version from file
    try:
        with open('version', 'r') as version_file:
            bot_version = version_file.read().strip()
    except FileNotFoundError:
        bot_version = "Unknown"

    # Get bot name
    bot_name = context.bot.username

    # Prepare the message
    message = (
        f"<b>{bot_name} v.{bot_version}</b> \n\n"
        f"<b>OS:</b> {os_name} {os_version}\n"
        f"<b>Kernel Version:</b> {kernel_version}\n"
        f"<b>System Uptime:</b> {uptime_str}\n\n"
        f"<b>CPU Usage:</b> {cpu_percent}%\n"
        f"<b>RAM Usage:</b> {ram_percent}%\n\n"
        f"<b>Total Memory:</b> {total_memory / (1024 ** 3):.2f} GB\n"
        f"<b>Available Memory:</b> {available_memory / (1024 ** 3):.2f} GB"
    )

    # Send the message privately
    context.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    # Notify in the chat that the information was sent
    update.message.reply_text("System information has been sent to your private messages.", parse_mode='HTML')


def clean(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if the user is an admin
    is_admin = False
    admins = context.bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            is_admin = True
            break

    # Check if the user is a hidden admin
    is_hidden_admin = False
    for event in context.dispatcher.chat_data.get(chat_id, {}).get('hidden_admin_events', []):
        if isinstance(event,
                      ChatMemberUpdated) and event.chat.id == chat_id and event.new_chat_member.user.id == user_id:
            is_hidden_admin = event.new_chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
            break

    # If the user is neither an admin nor a hidden admin, deny access
    if not is_admin and not is_hidden_admin:
        update.message.reply_text("You must be an admin to use this command.")
        return

    try:
        deleted_accounts = []
        for member in context.bot.get_chat_administrators(chat_id):
            if member.user.first_name == "Deleted Account":
                deleted_accounts.append(member.user.id)
                context.bot.kick_chat_member(chat_id, member.user.id)
                logging.info(f"Kicked deleted account: {member.user.id}")

        update.message.reply_text(f"Cleaned up {len(deleted_accounts)} deleted accounts.")
        logging.info(f"Cleaned {len(deleted_accounts)} deleted accounts from chat {chat_id}.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
        logging.error(f"Error cleaning deleted accounts: {e}")
