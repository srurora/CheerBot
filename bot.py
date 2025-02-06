import re, requests
import telebot
from telebot import types
import logging
from config import API_TOKEN
from scheduler import schedule_daily_affirmations
from db import save_user_preference

bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = "Welcome to CheerBot! 🌟\nI’ll send you daily affirmations to keep you motivated."
    bot.send_message(message.chat.id, welcome_text)

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

def is_valid_time(time_str):
    """Check if time is in HH:MM format (24-hour)."""
    return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_str))

def save_time_and_schedule(chat_id, time_str):
    """Save user preference in the database and schedule the message."""
    save_user_preference(chat_id, time_str)
    bot.send_message(chat_id, f"Got it! ✅ You'll receive affirmations daily at {time_str}.")

    schedule_daily_affirmations()

bot.infinity_polling()
