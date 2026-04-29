import telebot
import requests
import threading
import time
from flask import Flask
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
TOKEN = '8668800182:AAE-kJBsWhc7WY_Z6iwuDMirGnLfqfrBiBo'
CHAT_ID = '8596173679'
URL_WEB = 'https://kiniemlop92.pages.dev/'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Trang chủ web server (để Render không báo lỗi)
@app.route('/')
def index():
    return "Bot Uptime is running 24/7!"

def check_website():
    try:
        res = requests.get(URL_WEB, timeout=10)
        return "Online ✅" if res.status_code == 200 else f"Offline ❌ ({res.status_code})"
    except:
        return "Offline ❌ (Lỗi kết nối)"

# --- 5 LỆNH SLASH COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Chào Nhựt! Bot đã online trên Render.\nSử dụng /help để xem các lệnh.")

@bot.message_handler(commands=['check'])
def check(message):
    status = check_website()
    bot.reply_to(message, f"📊 **Trạng thái**: {URL_WEB}\n⚡ Kết quả: {status}", parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, f"ℹ️ **Thông tin**:\n- Hosting: Render\n- Web theo dõi: {URL_WEB}\n- Admin: Nhutcoder", parse_mode='Markdown')

@bot.message_handler(commands=['time'])
def get_time(message):
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz).strftime("%H:%M:%S - %d/%m/%Y")
    bot.reply_to(message, f"⏰ **Giờ VN**: {now}")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "/start - Bắt đầu\n/check - Kiểm tra web\n/info - Thông tin bot\n/time - Xem giờ\n/help - Hướng dẫn")

# --- HÀM TỰ ĐỘNG PING (Chạy ngầm) ---
def auto_ping():
    while True:
        status = check_website()
        if "Offline" in status:
            bot.send_message(CHAT_ID, f"🚨 **CẢNH BÁO**: {URL_WEB} đã sập!\nChi tiết: {status}")
        time.sleep(300) # Kiểm tra mỗi 5 phút

# --- CHẠY BOT ---
if __name__ == "__main__":
    # Chạy vòng lặp kiểm tra web trong một luồng riêng
    threading.Thread(target=auto_ping, daemon=True).start()
    
    # Chạy Web Server và Bot Polling
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
