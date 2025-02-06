from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import logging
import requests
import telebot
from config import API_TOKEN
from db import get_all_users

bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Denver"))
scheduler.start()
logger.info("Scheduler started. Affirmations will be sent daily.")

def send_affirmation(chat_id):
    """Fetch and send an affirmation to a user."""
    try:
        logger.info(f"Fetching affirmation for chat_id: {chat_id}")
        resp = requests.get("https://www.affirmations.dev/")
        if resp.status_code == 200:
            affirmation = resp.json().get("affirmation", "You are doing great! 😊")
        else:
            affirmation = "Stay positive and keep shining! ✨"
        
        bot.send_message(chat_id, affirmation)
        logger.info(f"Affirmation sent to chat_id: {chat_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching affirmation: {e}")
        bot.send_message(chat_id, "Oops! Couldn't fetch an affirmation right now. Try again later! 🚀")

def schedule_daily_affirmations():
    """Schedule affirmations for all users based on their stored preferences."""
    users = get_all_users()
    for chat_id, time_str in users:
        hour, minute = map(int, time_str.split(":"))
        scheduler.add_job(send_affirmation, "cron", hour=hour, minute=minute, args=[chat_id], id=str(chat_id), replace_existing=True)

schedule_daily_affirmations()
