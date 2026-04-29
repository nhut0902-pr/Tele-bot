import telebot
import requests
import threading
import time
import os
from flask import Flask
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
TOKEN = '8668800182:AAE-kJBsWhc7WY_Z6iwuDMirGnLfqfrBiBo'
CHAT_ID = '8596173679'
URL_WEB = 'https://kiniemlop92.pages.dev/'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Server Flask giúp Render duy trì dịch vụ
@app.route('/')
def index():
    return "Bot Uptime is running 24/7!"

def check_website():
    try:
        # Giả lập trình duyệt để tránh bị Cloudflare chặn
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(URL_WEB, headers=headers, timeout=15)
        if res.status_code == 200:
            return "Online ✅"
        else:
            return f"Offline ❌ (Mã lỗi: {res.status_code})"
    except Exception as e:
        return f"Offline ❌ (Lỗi kết nối)"

# --- XỬ LÝ LỆNH TELEGRAM ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🚀 **Bot Uptime Đã Sẵn Sàng!**\nChào Nhựt, bot đã online trên Render.\n\nDùng /help để xem danh sách lệnh.", parse_mode='Markdown')

@bot.message_handler(commands=['check'])
def check_cmd(message):
    status = check_website()
    bot.reply_to(message, f"📊 **Trạng thái**: {URL_WEB}\n⚡ Kết quả: {status}", parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def info_cmd(message):
    bot.reply_to(message, f"ℹ️ **Thông tin hệ thống**:\n- Hosting: Render.com\n- Website: {URL_WEB}\n- Tần suất check: 5 phút/lần\n- Dev: Nhutcoder", parse_mode='Markdown')

@bot.message_handler(commands=['time'])
def time_cmd(message):
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz).strftime("%H:%M:%S - %d/%m/%Y")
    bot.reply_to(message, f"⏰ **Thời gian hiện tại**: \n`{now}`", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = (
        "📌 **Danh sách lệnh**:\n"
        "/start - Khởi động bot\n"
        "/check - Kiểm tra web ngay\n"
        "/info - Thông tin bot\n"
        "/time - Xem giờ Việt Nam\n"
        "/help - Hướng dẫn này"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

# --- HÀM TỰ ĐỘNG KIỂM TRA (5 PHÚT/LẦN) ---
def auto_ping():
    while True:
        status = check_website()
        if "Offline" in status:
            # Gửi cảnh báo nếu phát hiện web sập
            bot.send_message(CHAT_ID, f"🚨 **CẢNH BÁO KHẨN CẤP**\nWebsite {URL_WEB} hiện không thể truy cập!\nTrạng thái: {status}", parse_mode='Markdown')
        time.sleep(300) # 300 giây = 5 phút

# --- CHẠY HỆ THỐNG ---
if __name__ == "__main__":
    # 1. Xóa Webhook cũ để tránh lỗi 409 Conflict
    try:
        bot.delete_webhook()
        print("Đã xóa Webhook cũ, chuyển sang chế độ Polling...")
    except:
        pass

    # 2. Chạy luồng kiểm tra web tự động (Background Thread)
    threading.Thread(target=auto_ping, daemon=True).start()
    
    # 3. Chạy luồng nhận lệnh Telegram (Polling)
    threading.Thread(target=lambda: bot.polling(none_stop=True, interval=1, timeout=20), daemon=True).start()
    
    # 4. Chạy Web Server (Cổng 10000 mặc định của Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
