from aiogram import Router
from aiogram.types import Message
from aiogram import types
from data.news import get_latest_crypto_news
from aiogram import F
from aiogram.enums.parse_mode import ParseMode


router = Router()

@router.message(F.text == "📰 Последние новости")
async def send_latest_news(message: Message):
    news = get_latest_crypto_news()
    
    if not news:
        await message.answer("К сожалению, не удалось получить новости на данный момент.")
    else:
        for article in news:
            await message.answer(article, parse_mode=ParseMode.HTML)
