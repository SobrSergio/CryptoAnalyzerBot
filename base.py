from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters.command import Command

router = Router()

user_request = {}

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: Message):
    
    kb = [
        [
            types.KeyboardButton(text="📊 Анализ данных"),
            types.KeyboardButton(text="🔔 Уведомления"),
            types.KeyboardButton(text="📰 Последние новости"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите команду",
        one_time_keyboard=False
    )
    
    await message.answer("""Привет!👋

Я бот 🤖, разработанный для определения паттернов поведения на основе индикаторов криптовалют и технического анализа.

Для начала работы воспользуйтесь кнопками:

📊 Анализ данных - для проведения анализа текущих данных.

🔔 Уведомления - для подписки на уведомления о сигналах покупки или продажи.""",
                         reply_markup=keyboard)

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("""🆘 Помощь

Написать создателю о ошибке и т.д🧑‍💻:
Telegram - @dev_ninjas""")
