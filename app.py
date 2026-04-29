import telebot
import requests
import threading
import time
import os
import psutil # Cần thêm vào requirements.txt
from flask import Flask
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
TOKEN = '8668800182:AAE-kJBsWhc7WY_Z6iwuDMirGnLfqfrBiBo'
CHAT_ID = '8596173679'
URL_WEB = 'https://kiniemlop92.pages.dev/'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot Uptime is running 24/7!"

def check_website():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        start_time = time.time()
        res = requests.get(URL_WEB, headers=headers, timeout=15)
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        if res.status_code == 200:
            return f"Online ✅", latency
        else:
            return f"Offline ❌ ({res.status_code})", 0
    except:
        return "Offline ❌ (Lỗi kết nối)", 0

# --- CÁC LỆNH MỚI THEO YÊU CẦU ---

# 1. Ping của Web
@bot.message_handler(commands=['webping'])
def web_ping(message):
    status, latency = check_website()
    bot.reply_to(message, f"🌐 **Web Latency**: `{latency}ms`\n📊 **Trạng thái**: {status}", parse_mode='Markdown')

# 2. Ping của Bot
@bot.message_handler(commands=['botping'])
def bot_ping(message):
    start_time = time.time()
    msg = bot.reply_to(message, "⚡ Đang đo độ trễ...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000)
    bot.edit_message_text(f"🚀 **Bot Latency**: `{latency}ms`\n📡 **Máy chủ**: Render (Singapore/Oregon)", msg.chat.id, msg.message_id, parse_mode='Markdown')

# 3. Trạng thái Server (Lệnh mới 1)
@bot.message_handler(commands=['server'])
def server_status(message):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    uptime = datetime.now().strftime("%H:%M:%S")
    bot.reply_to(message, f"🖥 **Thông số Server**:\n- CPU: `{cpu}%`\n- RAM: `{ram}%`\n- Up at: `{uptime}`", parse_mode='Markdown')

# 4. Gửi lời nhắn cho Admin (Lệnh mới 2)
@bot.message_handler(commands=['contact'])
def contact_admin(message):
    bot.reply_to(message, "📩 Bạn có thể liên hệ Admin qua: @Nhutcoder\nHoặc gửi email: nhut@example.com")

# 5. Giải trí - Conan Fact (Lệnh mới 3 - Theo sở thích của bạn)
@bot.message_handler(commands=['conan'])
def conan_fact(message):
    facts = [
        "Bạn có biết? Shinichi và Kaito Kid thực ra có ngoại hình giống hệt nhau.",
        "Tên của Conan được ghép từ Arthur Conan Doyle và Edogawa Ranpo.",
        "Tổ chức Áo đen có mục tiêu thực sự vẫn còn là một bí ẩn lớn."
    ]
    import random
    bot.reply_to(message, f"🕵️‍♂️ **Thám tử Conan**: {random.choice(facts)}")

# --- CÁC LỆNH CŨ ---
@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    text = (
        "📌 **Danh sách lệnh hiện có**:\n"
        "/check - Trạng thái web\n"
        "/webping - Đo độ trễ Website\n"
        "/botping - Đo độ trễ của Bot\n"
        "/server - Xem sức mạnh máy chủ\n"
        "/time - Giờ Việt Nam\n"
        "/conan - Một sự thật về Conan\n"
        "/contact - Liên hệ hỗ trợ"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

# --- CHẠY HỆ THỐNG ---
def auto_ping():
    while True:
        status, _ = check_website()
        if "Offline" in status:
            bot.send_message(CHAT_ID, f"🚨 **CẢNH BÁO**: {URL_WEB} đang sập!")
        time.sleep(300)

if __name__ == "__main__":
    try: bot.delete_webhook() 
    except: pass
    
    threading.Thread(target=auto_ping, daemon=True).start()
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
