import telebot

# Твой токен
BOT_TOKEN = '8902677080:AAHF_NagzxIiqE4rfA5cicuYba0js9gKxxw'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('*повтори '))
def repeat_and_delete(message):
    try:
        # Извлекаем текст после "*повтори "
        # 9 - это длина строки "*повтори "
        text_to_repeat = message.text[9:].strip()
        
        if text_to_repeat:
            # 1. Отправляем текст от имени бота
            bot.send_message(message.chat.id, text_to_repeat)
            
            # 2. Удаляем сообщение пользователя
            bot.delete_message(message.chat.id, message.message_id)
        else:
            # Если текста нет, можно просто ответить или проигнорировать
            bot.reply_to(message, "После команды нужно написать текст!")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()