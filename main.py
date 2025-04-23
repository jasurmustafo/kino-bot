import telebot
from flask import Flask
from threading import Thread
from replit.object_storage import Client
import time

# Flask server
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=5000)

def start_keep_alive():
    t = Thread(target=run)
    t.start()

# Bot sozlamalari
BOT_TOKEN = "7754771429:AAHjlYoRLHYu3C5z5HauI6K9F0wT39tRbVs"
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 7826580867
REQUIRED_CHANNELS = ["@Greenkarta_anketa", "@mustafokiyim"]

# Object Storage
storage = Client()

# Ma'lumotlarni yuklash
try:
    db = eval(storage.download_from_text("movies_db"))
except:
    db = {}

try:
    users = set(eval(storage.download_from_text("users_db")))
except:
    users = set()

# Ma'lumotlarni saqlash
def save_data():
    try:
        storage.upload_from_text("movies_db", str(db))
        storage.upload_from_text("users_db", str(list(users)))
    except Exception as e:
        print(f"Saqlashda xatolik: {e}")

# 24 soatcha avtomatik saqlash
save_thread = Thread(target=lambda: [time.sleep(86400), save_data()])
save_thread.start()

# Admin buyruqlar ro'yxati
ADMIN_COMMANDS = """
Admin buyruqlar:

1. Kino qo'shish:
   1️⃣ Kinoni yuboring
   2️⃣ "Kod berish" tugmasini bosing
   3️⃣ Kino uchun kod yuboring

2. Kodlarni ko'rish:
   - /kodlar buyrug'ini bosing

3. Reklama yuborish:
   - /reklama <xabar> buyrug'i orqali
"""

# Start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"Admin panelga xush kelibsiz!\n{ADMIN_COMMANDS}")
        return

    users.add(message.from_user.id)
    save_data()

    if is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "Kino kodini yuboring 🎬")
    else:
        channels = "\n".join(REQUIRED_CHANNELS)
        bot.reply_to(message, f"Botdan foydalanish uchun kanallarga obuna bo'ling:\n\n{channels}")

# Obuna tekshirish
def is_user_subscribed(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# Botni ishga tushirish
if __name__ == "__main__":
    try:
        start_keep_alive()
        print("Bot ishga tushdi!")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Xatolik: {e}")
        time.sleep(5)
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
