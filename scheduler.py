from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import logging
import requests
import telebot
from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Denver"))
scheduler.start()
logger.info("Scheduler started. Affirmations will be sent daily.")

def send_affirmation(chat_id):
    """Fetch and send a daily affirmation to the user."""
    try:
        logger.info(f"Fetching affirmation for chat_id: {chat_id}")
        resp = requests.get("https://www.affirmations.dev/")
        if resp.status_code == 200:
            affirmation = resp.json().get("affirmation", "You are doing great! 😊")
            logger.info(f"Affirmation fetched: {affirmation}")
        else:
            affirmation = "Stay positive and keep shining! ✨"
            logger.warning(f"Failed to fetch affirmation, using fallback: {affirmation}")
        
        bot.send_message(chat_id, affirmation)
        logger.info(f"Affirmation sent to chat_id: {chat_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching affirmation: {e}")
        bot.send_message(chat_id, "Oops! Couldn't fetch an affirmation right now. Try again later! 🚀")
        logger.error(f"Error message sent to chat_id: {chat_id}")

def schedule_daily_affirmation(chat_id, time_str):
    """Schedule a job to send a daily affirmation at the chosen time."""
    hour, minute = map(int, time_str.split(":"))
    scheduler.add_job(send_affirmation, "cron", hour=hour, minute=minute, args=[chat_id], id=str(chat_id), replace_existing=True)
