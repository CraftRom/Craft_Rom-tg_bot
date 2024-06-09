import logging
import platform
import time

import psutil
import requests
from telegram import Update
from telegram.ext import CallbackContext
from utils import save_topic_id, load_topic_id, is_user_admin, extract_files_list

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'  # Файл, в который будут записываться логи
)

# Глобальна змінна для зберігання ідентифікатора топіка
proposal_thread_id = load_topic_id()


# Команда для встановлення ідентифікатора топіка (доступна тільки адміністраторам)
async def set_topic(update: Update, context: CallbackContext):
    global proposal_thread_id
    user = update.effective_user

    chat_id = update.effective_chat.id
    if is_user_admin(update, context, user.id, chat_id):
        try:
            proposal_thread_id = int(context.args[0])
            await save_topic_id(proposal_thread_id)  # Збереження ідентифікатора у файл
            await update.message.reply_text(f"Ідентифікатор топіка для пропозицій встановлено: {proposal_thread_id}")
        except (IndexError, ValueError):
            await update.message.reply_text("Будь ласка, вкажіть дійсний ідентифікатор топіка.")
    else:
        await update.message.reply_text("Ви не маєте прав для виконання цієї команди.")


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
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


async def rom(update: Update, context: CallbackContext) -> None:
    device_code = context.args[0] if context.args else None

    try:
        response = requests.get('https://raw.githubusercontent.com/craftrom-os/official_devices/master/devices.json')
        response.raise_for_status()
        devices_data = response.json()
    except requests.RequestException as e:
        await update.message.reply_text(f"<b>Error:</b> {e}", parse_mode='HTML')
        logging.error(f"Error fetching devices data: {e}")
        return

    if not device_code:
        if not devices_data:
            await update.message.reply_text("Device code list is empty or not found.")
        else:
            device_codes = [device['codename'] for device in devices_data]
            device_codes_str = ", ".join(device_codes)
            await update.message.reply_text(
                '<b>Please specify the device code.</b>\n'
                'Example: <code>/rom onclite</code>\n'
                'You can also use <code>/rom</code> to get a list of supported devices.\n\n'
                '<b>List of supported device codes:</b>\n' + device_codes_str,
                parse_mode='HTML'
            )
        return

    device = next((d for d in devices_data if d.get('codename') == device_code), None)
    if not device:
        await update.message.reply_text(f"<b>Device code {device_code} not found.</b>", parse_mode='HTML')
        logging.warning(f"Device code {device_code} not found.")
        return

    name = device.get('name')
    brand = device.get('brand')
    maintainers = device.get('maintainers', 'No maintainers')
    supported_versions = device.get('supported_versions', [])
    latest_versions = supported_versions[-2:] if len(supported_versions) >= 2 else supported_versions

    versions_text_list = []
    for version in latest_versions:
        version_code = version.get('version_code')
        sf_url = f"https://sourceforge.net/projects/craftrom/files/{device_code}/{version_code}/"
        version_code = version_code.replace("thrall", "thrall (Android 13)").replace("uther", "uther (Android 14)")
        stable = version.get('stable')
        deprecated = version.get('deprecated')
        version_status = "Stable" if stable else "Unstable"
        if deprecated:
            version_status += " (Deprecated)"

        try:
            files_list = extract_files_list(sf_url)
            if files_list:
                file_info = files_list[0]
                versions_text_list.append(
                    f'▪️<b>Version:</b> {version_code}\n'
                    f' • <i>Date:</i> {file_info.last_updated}\n'
                    f' • <i>Status:</i> {version_status}\n'
                    f' • <i>Download:</i> <a href="{file_info.download_link}">{file_info.name}</a> ({file_info.size})'
                )
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
    await update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
    logging.info(f"Device info sent for device code {device_code}.")


async def system_info(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_user_admin(update, context, user_id, chat_id):
        await update.message.reply_text("You must be an admin to use this command.")
        return

    uptime = time.time() - psutil.boot_time()
    uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime))
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024 ** 3)
    available_memory = memory_info.available / (1024 ** 3)
    os_name = platform.system()
    os_version = platform.version()
    kernel_version = platform.release()

    try:
        with open('version', 'r') as version_file:
            bot_version = version_file.read().strip()
    except FileNotFoundError:
        bot_version = "Unknown"

    bot_name = context.bot.username
    message = (
        f"<b>{bot_name} v.{bot_version}</b> \n\n"
        f"<b>OS:</b> {os_name} {os_version}\n"
        f"<b>Kernel Version:</b> {kernel_version}\n"
        f"<b>System Uptime:</b> {uptime_str}\n\n"
        f"<b>CPU Usage:</b> {cpu_percent}%\n"
        f"<b>RAM Usage:</b> {ram_percent}%\n\n"
        f"<b>Total Memory:</b> {total_memory:.2f} GB\n"
        f"<b>Available Memory:</b> {available_memory:.2f} GB"
    )

    await context.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    await update.message.reply_text("System information has been sent to your private messages.", parse_mode='HTML')


async def clean(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_user_admin(update, context, user_id, chat_id):
        await update.message.reply_text("You must be an admin to use this command.")
        return

    try:
        deleted_accounts = [member.user.id for member in context.bot.get_chat_administrators(chat_id) if
                            member.user.first_name == "Deleted Account"]
        for user_id in deleted_accounts:
            context.bot.kick_chat_member(chat_id, user_id)
            logging.info(f"Kicked deleted account: {user_id}")

        await update.message.reply_text(f"Cleaned up {len(deleted_accounts)} deleted accounts.")
        logging.info(f"Cleaned {len(deleted_accounts)} deleted accounts from chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logging.error(f"Error cleaning deleted accounts: {e}")
