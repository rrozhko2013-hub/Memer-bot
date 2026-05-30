import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8902677080:AAHF_NagzxIiqE4rfA5cicuYba0js9gKxxw"

# Состояния для ConversationHandler
WAITING_FOR_IMAGE = 1
WAITING_FOR_TEXT = 2

# Смешные автоматические текст для мемов
FUNNY_TEXTS = [
    ("КОГДА ПОНИМАЕШЬ", "ЧТО ЗАБЫЛ ДОМАШКУ"),
    ("МОЙ КОД", "В ПРОДАКШЕНЕ"),
    ("Я:", "ТАКЖЕ Я:"),
    ("ОЖИДАНИЯ", "РЕАЛЬНОСТЬ"),
    ("МОМ:", "ЧТО ТЫ ДЕЛАЕШЬ"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартовая команда"""
    await update.message.reply_text(
        "🎨 Привет! Я бот для создания мемов!\n\n"
        "Команды:\n"
        "/start - Начать\n"
        "/help - Помощь\n\n"
        "Или просто напиши: 'Мемер создай мем'"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда помощи"""
    await update.message.reply_text(
        "📖 Как использовать:\n\n"
        "1️⃣ Напиши: 'Мемер создай мем'\n"
        "2️⃣ Отправь картинку\n"
        "3️⃣ (Опционально) Напиши текст для мема\n"
        "4️⃣ Получи готовый мем!\n\n"
        "Если не указать текст - буду использовать смешные автотексты 😄"
    )

async def meme_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка команды 'Мемер создай мем'"""
    await update.message.reply_text(
        "📸 Отлично! Отправь мне картинку, которую хочешь превратить в мем!"
    )
    return WAITING_FOR_IMAGE

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка загруженной картинки"""
    try:
        # Скачиваем картинку
        file = await update.message.photo[-1].get_file()
        image_bytes = await file.download_as_bytearray()
        
        # Сохраняем в контексте для следующего шага
        context.user_data['image_bytes'] = image_bytes
        
        await update.message.reply_text(
            "✅ Картинка получена!\n\n"
            "Теперь напиши текст для мема (верхняя часть и нижняя через '|')\n\n"
            "Например: 'МОЙ КОД|В ПРОДАКШЕНЕ'\n\n"
            "Или просто напиши 'случайный' - буду использовать автотекст 😄"
        )
        return WAITING_FOR_TEXT
    except Exception as e:
        logger.error(f"Ошибка при загрузке картинки: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке картинки. Попробуй ещё раз.")
        return ConversationHandler.END

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка текста для мема"""
    try:
        user_text = update.message.text.strip()
        image_bytes = context.user_data.get('image_bytes')
        
        if not image_bytes:
            await update.message.reply_text("❌ Картинка не найдена. Начни заново.")
            return ConversationHandler.END
        
        # Открываем картинку
        image = Image.open(BytesIO(image_bytes))
        
        # Определяем текст
        if user_text.lower() == "случайный":
            top_text, bottom_text = FUNNY_TEXTS[0]
        elif "|" in user_text:
            parts = user_text.split("|")
            top_text = parts[0].strip().upper()
            bottom_text = parts[1].strip().upper() if len(parts) > 1 else ""
        else:
            top_text = user_text.upper()
            bottom_text = ""
        
        # Создаём мем
        meme_image = create_meme(image, top_text, bottom_text)
        
        # Отправляем результат
        meme_bytes = BytesIO()
        meme_image.save(meme_bytes, format='PNG')
        meme_bytes.seek(0)
        
        await update.message.reply_photo(
            photo=meme_bytes,
            caption="🎉 Вот твой мем! Смешно? 😄"
        )
        
        # Очищаем контекст
        context.user_data.clear()
        
        await update.message.reply_text(
            "Хочешь создать ещё один мем?\n"
            "Напиши: 'Мемер создай мем'"
        )
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при создании мема: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        return ConversationHandler.END

def create_meme(image: Image.Image, top_text: str, bottom_text: str) -> Image.Image:
    """Создание мема из картинки и текста"""
    # Копируем изображение
    meme = image.copy()
    width, height = meme.size
    
    # Пытаемся найти шрифт
    try:
        # Для Linux/Mac
        font_size = int(height / 10)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            # Для Windows
            font = ImageFont.truetype("arial.ttf", int(height / 10))
        except:
            # Fallback на стандартный шрифт
            font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(meme)
    
    # Параметры текста
    text_color = "white"
    outline_color = "black"
    outline_width = 2
    
    # Добавляем верхний текст
    if top_text:
        draw_text_with_outline(
            draw, top_text, 
            (width // 2, height // 8),
            font, text_color, outline_color, outline_width
        )
    
    # Добавляем нижний текст
    if bottom_text:
        draw_text_with_outline(
            draw, bottom_text,
            (width // 2, height - height // 8),
            font, text_color, outline_color, outline_width
        )
    
    return meme

def draw_text_with_outline(draw, text: str, position, font, fill_color: str, 
                           outline_color: str, outline_width: int) -> None:
    """Рисует текст с контуром"""
    x, y = position
    
    # Рисуем контур
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            draw.text(
                (x + adj_x, y + adj_y), text,
                font=font, fill=outline_color, anchor="mm"
            )
    
    # Рисуем основной текст
    draw.text(position, text, font=font, fill=fill_color, anchor="mm")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    await update.message.reply_text("❌ Отменено. Напиши 'Мемер создай мем' для новой попытки.")
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка простых сообщений"""
    text = update.message.text.lower()
    
    if "мемер" in text and "создай" in text and "мем" in text:
        return await meme_request(update, context)
    else:
        await update.message.reply_text(
            "Я тебя не понял 🤔\n\n"
            "Напиши: 'Мемер создай мем'\n"
            "или используй /help для справки"
        )
        return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    # Создаём приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler для процесса создания мема
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        ],
        states={
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, handle_image),
                CommandHandler("cancel", cancel),
            ],
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
                CommandHandler("cancel", cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
