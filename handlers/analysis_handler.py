import os
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import types

from data.analysis import fetch_cryptocurrency_data, generate_analysis_report, generate_chart
from aiogram import F
from binance.client import Client


binance_client = Client()
valid_intervals = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]

def get_popular_pairs():
    tickers = binance_client.get_ticker()
    tickers_sorted = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
    popular_pairs = [ticker['symbol'] for ticker in tickers_sorted if ticker['symbol'].endswith('USDT')][:6]
    popular_pairs_with_slash = [f"{pair[:-4]}/{pair[-4:]}" for pair in popular_pairs]
    return popular_pairs_with_slash

router = Router()

class Reg(StatesGroup):
    crypto = State()
    interval = State()
    visualization = State()

@router.message(F.text == "📊 Анализ данных")
async def analyze_command(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(Reg.crypto)
    
    popular_pairs = get_popular_pairs()
    kb = [
        [types.KeyboardButton(text=pair) for pair in popular_pairs[:3]],
        [types.KeyboardButton(text=pair) for pair in popular_pairs[3:]]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите популярную пару или введите свою",
        one_time_keyboard=False
    )
    
    await message.answer("💰 Введите название криптовалюты для анализа (В виде пары, например BTC/USDT): ", reply_markup=keyboard)


@router.message(Reg.crypto)
async def analyze_crypto(message: Message, state: FSMContext):
    crypto_pair = message.text
    if '/' not in crypto_pair:
        await message.answer("❌ Неверный формат ввода. Пожалуйста, введите название криптовалютной пары в правильном формате (например, BTC/USDT).")
        return

    await state.update_data(crypto=crypto_pair)
    await state.set_state(Reg.interval)
    kb = [
        [types.KeyboardButton(text="1m"), types.KeyboardButton(text="5m"), types.KeyboardButton(text="15m")],
        [types.KeyboardButton(text="30m"), types.KeyboardButton(text="1h"), types.KeyboardButton(text="4h")],
        [types.KeyboardButton(text="1d"), types.KeyboardButton(text="1w"), types.KeyboardButton(text="1M")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите интервал",
        one_time_keyboard=False
    )

    await message.answer("Выберите интервал: ", reply_markup=keyboard)

@router.message(Reg.interval)
async def analyze_interval(message: Message, state: FSMContext):
    interval = message.text
    if interval not in valid_intervals:
        await message.answer("❌ Неверный интервал. Пожалуйста, выберите один из допустимых интервалов.")
        return

    await state.update_data(interval=interval)
    await state.set_state(Reg.visualization)
    kb = [
        [types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Отправить визуализацию графика?",
        one_time_keyboard=False
    )

    await message.answer("Отправить визуализацию графика?", reply_markup=keyboard)



@router.message(Reg.visualization)
async def analyze_visualization(message: Message, state: FSMContext):
    visualize = message.text.lower()
    if visualize not in ["да", "нет"]:
        await message.answer("❌ Пожалуйста, выберите 'Да' или 'Нет'.")
        return

    data = await state.get_data()
    await state.clear()

    wait_message = await message.answer("Пожалуйста, подождите... ⏳", reply_markup=types.ReplyKeyboardRemove())
    await message.bot.send_chat_action(message.chat.id, 'typing')
    pro_analyze, support_level, resistance_level = generate_analysis_report(data['crypto'], data['interval'])

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

    if visualize == "да":
        ohlcv_data = fetch_cryptocurrency_data(data['crypto'], data['interval'])
        chart_path = generate_chart(data['crypto'], data['interval'], ohlcv_data, support_level, resistance_level)
    
    
    await message.bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)
    
    await message.answer(f"{pro_analyze}", reply_markup=keyboard)
    if visualize == "да":
        await message.answer_photo(photo=types.FSInputFile(chart_path), caption="Вот твой график анализа.")
        os.remove(chart_path)
        