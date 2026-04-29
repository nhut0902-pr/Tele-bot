import telebot
import requests
import time
import os
from datetime import datetime
import pytz

# Cấu hình thông tin (Nên dùng Secret để bảo mật)
TOKEN = '8668800182:AAE-kJBsWhc7WY_Z6iwuDMirGnLfqfrBiBo'
CHAT_ID = '8596173679'
URL_WEB = 'https://kiniemlop92.pages.dev/'

bot = telebot.TeleBot(TOKEN)

def check_website():
    try:
        response = requests.get(URL_WEB, timeout=10)
        if response.status_code == 200:
            return "Online ✅"
        else:
            return f"Offline ❌ (Code: {response.status_code})"
    except:
        return "Offline ❌ (Không thể kết nối)"

# --- 5 Lệnh Slash Commands ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 Bot Uptime GitHub Action đã sẵn sàng!\nSử dụng /help để xem lệnh.")

@bot.message_handler(commands=['check'])
def manual_check(message):
    status = check_website()
    bot.reply_to(message, f"📊 **Trạng thái**: {URL_WEB}\n⚡ Kết quả: {status}", parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = (
        "ℹ️ **Thông tin Bot**:\n"
        "- Chạy trên: GitHub Actions\n"
        "- Website theo dõi: kiniemlop92.pages.dev\n"
        "- Admin: Nhutcoder"
    )
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['time'])
def send_time(message):
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz).strftime("%H:%M:%S - %d/%m/%Y")
    bot.reply_to(message, f"⏰ **Giờ Việt Nam**: {now}")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📌 **Danh sách lệnh**:\n"
        "/start - Khởi động\n"
        "/check - Kiểm tra web\n"
        "/info - Thông tin bot\n"
        "/time - Xem giờ hệ thống\n"
        "/help - Hướng dẫn"
    )
    bot.reply_to(message, help_text)

# --- Chạy kiểm tra tự động 1 lần (Cho Action) ---
if __name__ == "__main__":
    # Nếu chạy qua GitHub Action (workflow), nó sẽ check web và báo nếu sập
    status = check_website()
    if "Offline" in status:
        bot.send_message(CHAT_ID, f"🚨 **CẢNH BÁO**: {URL_WEB} đang sập!\n{status}", parse_mode='Markdown')
    
    # Để bot nhận được lệnh liên tục, bạn cần chạy bot.polling()
    # Tuy nhiên GitHub Action free chỉ nên dùng để check theo lịch.
    # Nếu bạn muốn bot TRỰC LỆNH 24/7, hãy bỏ comment dòng dưới:
    bot.polling(none_stop=True)
