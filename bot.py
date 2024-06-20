import asyncio
from aiogram import Bot, Dispatcher

from config import TELEGRAM_TOKEN
from handlers import analysis_handler, notifications_handler, news_handler
import base
from colorama import init, Fore, Style
from models import SessionLocal
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

init(autoreset=True)
# Информация о боте
BOT_NAME = "CryptoAnalyzerBot"
BOT_USERNAME = "@CryptoAnalyzerBot"
BOT_VERSION = "1.0"

# Приветственное сообщение
welcome_message = f"{Fore.GREEN}Бот '{BOT_NAME}' ({BOT_USERNAME}) версии {BOT_VERSION} успешно запущен!{Style.RESET_ALL}"


bot = Bot(token=TELEGRAM_TOKEN)

#обработчик всех сообщений и событий телеграмм бота!
dp = Dispatcher()
    
#создание бота
async def main():
    #регитсрация обработчиков
    dp.include_router(base.router)
    dp.include_router(analysis_handler.router)
    dp.include_router(notifications_handler.router)
    dp.include_router(news_handler.router)

    print(welcome_message)
    
    asyncio.create_task(notifications_handler.check_prices())
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
