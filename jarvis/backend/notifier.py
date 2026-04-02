from telegram import Bot

TOKEN = "your_token"
CHAT_ID = "your_chat_id"

bot = Bot(token=TOKEN)

def send_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)
