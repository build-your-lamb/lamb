import configparser
from telegram.ext import ApplicationBuilder, CommandHandler, filters
from livekit import api
import subprocess
import logging
import psutil

logging.basicConfig(level=logging.INFO)

MEET_URL = 'https://meet-chi-flax.vercel.app'
LIVEKIT_ROOM = 'room'
MEET_PROCESS_NAME = 'meet'

def load_config(file_path='config.ini'):
    config = configparser.ConfigParser()
    config.read(file_path)
    api_keys = {
        'livekit_url': config.get('api_keys', 'livekit_url', fallback=None),
        'livekit_api_key': config.get('api_keys', 'livekit_api_key', fallback=None),
        'livekit_api_secret': config.get('api_keys', 'livekit_api_secret', fallback=None),
        'telegram_bot_token': config.get('api_keys', 'telegram_bot_token', fallback=None),
    }
    return api_keys

def is_process_running(process_name):
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if process_name in proc.info['name'] or \
               any(process_name in s for s in proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def get_livekit_token(livekit_api_key, livekit_api_secret, user_id):
    token = api.AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(user_id) \
        .with_name(user_id) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=LIVEKIT_ROOM,
        )).to_jwt()
    return token


def launch_meet_process(livekit_url, livekit_token):
    cmd = [MEET_PROCESS_NAME, '-u', livekit_url, '-t', livekit_token]
    logging.info(f"Launching meet process with command: {' '.join(cmd)}")
    if is_process_running(MEET_PROCESS_NAME):
        logging.info("Process already running, not starting a new one.")
    else:
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            logging.error(f"Launching meet process failed: {e}")
            raise

async def join_command(update, context):
    keys = context.bot_data['api_keys']
    api_key = keys['livekit_api_key']
    api_secret = keys['livekit_api_secret']
    livekit_url = keys['livekit_url']

    bot_id = 'bot'
    bot_token = get_livekit_token(api_key, api_secret, bot_id)
    launch_meet_process(livekit_url, bot_token)
    await update.message.reply_text(f'Bot is joining')

async def meet_command(update, context):
    keys = context.bot_data['api_keys']
    api_key = keys['livekit_api_key']
    api_secret = keys['livekit_api_secret']
    livekit_url = keys['livekit_url']

    user_id = str(update.message.from_user.id)
    user_token = get_livekit_token(api_key, api_secret, user_id)
    meet_link = f'{MEET_URL}/custom?liveKitUrl={livekit_url}&token={user_token}'
    await update.message.reply_text(f'Click the link to join the meeting:\n{meet_link}')

def main():
    keys = load_config()
    bot_token = keys.get('telegram_bot_token')

    app = ApplicationBuilder().token(bot_token).build()
    app.bot_data['api_keys'] = keys

    app.add_handler(CommandHandler('join', join_command))
    app.add_handler(CommandHandler('meet', meet_command))

    print('Launching bot...')
    app.run_polling()

if __name__ == '__main__':
    main()
