TOKEN = "your_token"
CHAT_ID = "your_chat_id"

def send_alert(message):
    try:
        from telegram import Bot
        bot = Bot(token=TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"[NOTIFIER_FAIL] {e}")
