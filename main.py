import telebot
import os
from threading import Thread
from flask import Flask

# Твой токен Telegram
BOT_TOKEN = '8902677080:AAHF_NagzxIiqE4rfA5cicuYba0js9gKxxw'
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем мини веб-сервер для хостинга Render
app = Flask('')

@app.route('/')
def home():
    return "Бот активен и работает!"

def run_web_server():
    # Render автоматически передает порт в переменные окружения
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Хэндлер для команды повторения
@bot.message_handler(func=lambda message: message.text and message.text.startswith('*повтори '))
def repeat_and_delete(message):
    try:
        text_to_repeat = message.text[9:].strip()
        if text_to_repeat:
            bot.send_message(message.chat.id, text_to_repeat)
            bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении/отправке: {e}")

if __name__ == '__main__':
    print("Запуск веб-сервера для Render...")
    # Запускаем веб-сервер в отдельном потоке, чтобы Render не ругался на Timed Out
    server_thread = Thread(target=run_web_server)
    server_thread.start()
    
    print("Бот запущен в режиме polling!")
    bot.infinity_polling()