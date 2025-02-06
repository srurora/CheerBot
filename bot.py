import re, requests
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import logging
from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)
# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user_preferences = {}  # Store user preferences (chat_id -> time in HH:MM)

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = "Welcome to CheerBot! 🌟\nI’ll send you daily affirmations to keep you motivated. Created with love by Srushti!"
    bot.send_message(message.chat.id, welcome_text)

    # Ask the user when they want affirmations
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Morning ☀️ (8 AM)", callback_data="time_08:00"))
    markup.add(types.InlineKeyboardButton("Afternoon 🌤 (2 PM)", callback_data="time_14:00"))
    markup.add(types.InlineKeyboardButton("Evening 🌙 (8 PM)", callback_data="time_20:00"))
    markup.add(types.InlineKeyboardButton("Custom ⏰", callback_data="time_custom"))

    bot.send_message(message.chat.id, "When would you like to receive your daily affirmation?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def handle_time_selection(call):
    chat_id = call.message.chat.id

    if call.data == "time_custom":
        bot.send_message(chat_id, "Please type the time in HH:MM format (24-hour format, e.g., 15:30 for 3:30 PM).")
        bot.register_next_step_handler(call.message, save_custom_time)  
    else:
        time_selected = call.data.split("_")[1]  # Extract time (e.g., "08:00")
        save_time_and_schedule(chat_id, time_selected)

def save_custom_time(message):
    chat_id = message.chat.id
    custom_time = message.text.strip()

    if not is_valid_time(custom_time):
        bot.send_message(chat_id, "Invalid time format. Please enter in HH:MM format (24-hour).")
        bot.register_next_step_handler(message, save_custom_time)
        return

    save_time_and_schedule(chat_id, custom_time)

def save_time_and_schedule(chat_id, time_str):
    """Save user preference and schedule the message."""
    user_preferences[chat_id] = time_str
    bot.send_message(chat_id, f"Got it! ✅ You'll receive affirmations daily at {time_str}.")

    # Schedule the message
    schedule_daily_affirmation(chat_id, time_str)

def is_valid_time(time_str):
    """Check if time is in HH:MM format (24-hour)."""
    return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_str))

def send_affirmation(chat_id):
    try:
        logger.info(f"Fetching affirmation for chat_id: {chat_id}")
        resp = requests.get("https://www.affirmations.dev/")
        if resp.status_code == 200:
            affirmation = resp.json().get("affirmation", "You are doing great! 😊")
            logger.info(f"Affirmation fetched: {affirmation}")
        else:
            affirmation = "Stay positive and keep shining! ✨"  # Fallback message    
            logger.warning(f"Failed to fetch affirmation, using fallback: {affirmation}")
        
        bot.send_message(chat_id, affirmation)
        logger.info(f"Affirmation sent to chat_id: {chat_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching affirmation: {e}")
        bot.send_message(chat_id, "Oops! Couldn't fetch an affirmation right now. Try again later! 🚀")
        logger.error(f"Error message sent to chat_id: {chat_id}")

# Set the scheduler with the Mountain Time timezone
scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Denver"))
scheduler.add_job(send_affirmation, 'interval', hours=24, args=['chat_id_example'])

# Start the scheduler
scheduler.start()
logger.info("Scheduler started. Affirmations will be sent daily.")

def schedule_daily_affirmation(chat_id, time_str):
    """Schedule a job to send a daily affirmation at the chosen time."""
    hour, minute = map(int, time_str.split(":"))
    scheduler.add_job(send_affirmation, "cron", hour=hour, minute=minute, args=[chat_id], id=str(chat_id), replace_existing=True)

bot.polling()
