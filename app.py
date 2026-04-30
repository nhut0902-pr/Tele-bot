import telebot
import requests
import threading
import time
import os
import psutil
from flask import Flask
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

# --- CẤU HÌNH ---
TOKEN = '8668800182:AAE-kJBsWhc7WY_Z6iwuDMirGnLfqfrBiBo'
CHAT_ID = '8596173679'
URL_WEB = 'https://kiniemlop92.pages.dev/'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot Uptime & Crawler is running 24/7!"

# --- HÀM CRAWLER DỮ LIỆU ---
def crawl_web_content():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(URL_WEB, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Lấy tiêu đề trang (Title)
            title = soup.title.string if soup.title else "Không có tiêu đề"
            
            # Lấy các thẻ H1 hoặc đoạn văn đầu tiên để xem nội dung
            h1 = soup.find('h1').get_text() if soup.find('h1') else "Không có tiêu đề H1"
            
            # Đếm số lượng liên kết (thẻ a) trên trang
            links_count = len(soup.find_all('a'))
            
            return {
                "status": "Thành công",
                "title": title.strip(),
                "h1": h1.strip(),
                "links": links_count
            }
    except Exception as e:
        return {"status": "Lỗi", "detail": str(e)}

def check_website():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        start_time = time.time()
        res = requests.get(URL_WEB, headers=headers, timeout=15)
        latency = round((time.time() - start_time) * 1000)
        return ("Online ✅" if res.status_code == 200 else f"Offline ❌ ({res.status_code})"), latency
    except:
        return "Offline ❌ (Lỗi kết nối)", 0

# --- CÁC LỆNH BOT ---

@bot.message_handler(commands=['crawl'])
def crawl_cmd(message):
    msg = bot.reply_to(message, "🔍 Đang cào dữ liệu từ website...")
    data = crawl_web_content()
    
    if data["status"] == "Thành công":
        text = (
            f"📑 **Dữ liệu thu thập được**:\n"
            f"- **Tiêu đề**: `{data['title']}`\n"
            f"- **Nội dung chính**: `{data['h1']}`\n"
            f"- **Số lượng liên kết**: `{data['links']}`\n"
            f"🔗 [Truy cập web]({URL_WEB})"
        )
    else:
        text = f"❌ Không thể cào dữ liệu. Chi tiết: {data['detail']}"
    
    bot.edit_message_text(text, msg.chat.id, msg.message_id, parse_mode='Markdown', disable_web_page_preview=True)

@bot.message_handler(commands=['webping'])
def web_ping(message):
    status, latency = check_website()
    bot.reply_to(message, f"🌐 **Độ trễ Web**: `{latency}ms`\n📊 **Trạng thái**: {status}", parse_mode='Markdown')

@bot.message_handler(commands=['botping'])
def bot_ping(message):
    start_time = time.time()
    msg = bot.reply_to(message, "⚡...")
    latency = round((time.time() - start_time) * 1000)
    bot.edit_message_text(f"🚀 **Bot Latency**: `{latency}ms`", msg.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['server'])
def server_status(message):
    bot.reply_to(message, f"🖥 **Server**: CPU `{psutil.cpu_percent()}%` | RAM `{psutil.virtual_memory().percent}%`", parse_mode='Markdown')

@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    text = (
        "🤖 **Bot Quản Trị Lớp 9/2**\n\n"
        "/crawl - Cào dữ liệu từ trang kỷ niệm\n"
        "/check - Kiểm tra trạng thái web\n"
        "/webping - Đo tốc độ tải web\n"
        "/botping - Kiểm tra phản hồi bot\n"
        "/server - Thông số máy chủ Render\n"
        "/time - Giờ Việt Nam hiện tại"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['time'])
def time_cmd(message):
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz).strftime("%H:%M:%S - %d/%m/%Y")
    bot.reply_to(message, f"⏰ **Giờ VN**: `{now}`", parse_mode='Markdown')

# --- LUỒNG CHẠY HỆ THỐNG ---
def auto_ping():
    while True:
        status, _ = check_website()
        if "Offline" in status:
            try: bot.send_message(CHAT_ID, f"🚨 **SẬP WEB**: {URL_WEB}")
            except: pass
        time.sleep(300)

def run_bot():
    while True:
        try:
            bot.delete_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=auto_ping, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
