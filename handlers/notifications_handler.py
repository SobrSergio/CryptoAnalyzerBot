import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from models import SessionLocal, UserNotification
from data.analysis import fetch_current_price
from bot import bot
from aiogram import types
from binance.client import Client


router = Router()
binance_client = Client()

class NotificationStates(StatesGroup):
    waiting_for_crypto_pair = State()
    waiting_for_target_price = State()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_popular_pairs():
    tickers = binance_client.get_ticker()
    tickers_sorted = sorted(tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
    popular_pairs = [ticker['symbol'] for ticker in tickers_sorted if ticker['symbol'].endswith('USDT')][:6]
    popular_pairs_with_slash = [f"{pair[:-4]}/{pair[-4:]}" for pair in popular_pairs]
    return popular_pairs_with_slash


@router.message(F.text == "🔔 Уведомления")
async def notify_command(message: Message, state: FSMContext):
    
    await message.delete()
    await state.set_state(NotificationStates.waiting_for_crypto_pair)
    
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
    
    await message.answer("💰 Введите название криптовалюты для настройки уведомления (В виде пары, например BTC/USDT): ", reply_markup=keyboard)



@router.message(NotificationStates.waiting_for_crypto_pair)
async def process_crypto_pair(message: Message, state: FSMContext):
    
    await state.update_data(waiting_for_crypto_pair=message.text)
    await state.set_state(NotificationStates.waiting_for_target_price)
    
    await message.answer("📈 Введите цену или процент изменения: ", reply_markup=types.ReplyKeyboardRemove())



@router.message(NotificationStates.waiting_for_target_price)
async def process_target_price(message: Message, state: FSMContext):
    target = message.text
    user_data = await state.get_data()
    crypto_pair = user_data['waiting_for_crypto_pair']
    await state.clear()
    
    wait_message = await message.answer("Пожалуйста, подождите... ⏳", reply_markup=types.ReplyKeyboardRemove())
    await message.bot.send_chat_action(message.chat.id, 'typing')
    
    initial_price = fetch_current_price(crypto_pair)
    try:
        if target.endswith('%'):
            if target[0] in ('+', '-'):
                sign = 1 if target[0] == '+' else -1
                percentage = float(target[1:].rstrip('%'))
            else:
                sign = 1
                percentage = float(target.rstrip('%'))
            target_price = initial_price * (1 + sign * percentage / 100)
        else:
            target_price = float(target)

        db = next(get_db())
        user_notification = UserNotification(
            user_id=message.from_user.id,
            crypto_pair=crypto_pair,
            target_price=target_price,
            initial_price=initial_price
        )
        db.add(user_notification)
        db.commit()
        
        
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
        
        
        
        await message.bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)
        await message.answer(f"🔔 Уведомление установлено для {crypto_pair} на цену {target}.", reply_markup=keyboard)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену или процент.")
        
        
        
async def check_prices():
    while True:
        db = next(get_db())
        notifications = db.query(UserNotification).all()
        for notification in notifications:
            current_price = fetch_current_price(notification.crypto_pair)
            

            if abs(notification.target_price) > 1: 
                target_price = notification.initial_price * (1 + notification.target_price / 100)
                if notification.target_price > 0:
                    if current_price >= target_price:
                        await bot.send_message(notification.user_id, f"""🚨 Внимание 🚨
Цена {notification.crypto_pair} достигла или превысила {target_price}!""")
                        db.delete(notification)
                        db.commit()
                else:
                    if current_price <= target_price:
                        await bot.send_message(notification.user_id, f"""🚨 Внимание 🚨
Цена {notification.crypto_pair} достигла или упала ниже {target_price}!""")
                        db.delete(notification)
                        db.commit()
            else: 
                target_price = notification.target_price
                if current_price >= target_price:
                    await bot.send_message(notification.user_id, f"""🚨 Внимание 🚨
Цена {notification.crypto_pair} достигла или превысила {target_price}!""")
                    db.delete(notification)
                    db.commit()
                elif current_price <= target_price:
                    await bot.send_message(notification.user_id, f"""🚨 Внимание 🚨
Цена {notification.crypto_pair} упала до или ниже {target_price}!""")
                    db.delete(notification)
                    db.commit()
        
        await asyncio.sleep(20) 