import pandas as pd
import talib
import numpy as np
from datetime import datetime
import ccxt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import VotingRegressor
import os
import matplotlib.pyplot as plt
import mplfinance as mpf



pattern_codes = {
    "CDL2CROWS": "Два ворона",
    "CDL3BLACKCROWS": "Три черных ворона",
    "CDL3INSIDE": "Три внутри вверх/вниз",
    "CDL3LINESTRIKE": "Трехлинейный удар",
    "CDL3OUTSIDE": "Три снаружи вверх/вниз",
    "CDL3STARSINSOUTH": "Три звезды на юге",
    "CDL3WHITESOLDIERS": "Три продвигающихся белых солдата",
    "CDLABANDONEDBABY": "Заброшенный ребенок",
    "CDLADVANCEBLOCK": "Продвинутый блок",
    "CDLBELTHOLD": "Поясной захват",
    "CDLBREAKAWAY": "Перерыв",
    "CDLCLOSINGMARUBOZU": "Закрывающийся марубозу",
    "CDLCONCEALBABYSWALL": "Скрыть стену ребенка",
    "CDLCOUNTERATTACK": "Контратака",
    "CDLDARKCLOUDCOVER": "Темное облачное покрытие",
    "CDLDOJI": "Доджи",
    "CDLDOJISTAR": "Доджи-звезда",
    "CDLDRAGONFLYDOJI": "Доджи-стрекоза",
    "CDLENGULFING": "Поглощение",
    "CDLEVENINGDOJISTAR": "Вечерняя звезда доджи",
    "CDLEVENINGSTAR": "Вечерняя звезда",
    "CDLGAPSIDESIDEWHITE": "Пробел в сторону белого",
    "CDLGRAVESTONEDOJI": "Могильный доджи",
    "CDLHAMMER": "Молот",
    "CDLHANGINGMAN": "Повешенный человек",
    "CDLHARAMI": "Харами",
    "CDLHARAMICROSS": "Харами-крест",
    "CDLHIGHWAVE": "Высокая волна",
    "CDLHIKKAKE": "Хиккаке",
    "CDLHIKKAKEMOD": "Хиккаке мод",
    "CDLHOMINGPIGEON": "Домовой голубь",
    "CDLIDENTICAL3CROWS": "Три одинаковых ворона",
    "CDLINNECK": "На шее",
    "CDLINVERTEDHAMMER": "Обратный молот",
    "CDLKICKING": "Удар",
    "CDLKICKINGBYLENGTH": "Удар по длине",
    "CDLLADDERBOTTOM": "Лестничное дно",
    "CDLLONGLEGGEDDOJI": "Длинноногий доджи",
    "CDLLONGLINE": "Длинная линия",
    "CDLMARUBOZU": "Марубозу",
    "CDLMATCHINGLOW": "Соответствующий минимум",
    "CDLMATHOLD": "Мат холд",
    "CDLMORNINGDOJISTAR": "Утренняя звезда доджи",
    "CDLMORNINGSTAR": "Утренняя звезда",
    "CDLONNECK": "Один на шее",
    "CDLPIERCING": "Пронзительный",
    "CDLRICKSHAWMAN": "Рикша-человек",
    "CDLRISEFALL3METHODS": "Методы подъема/падения",
    "CDLSEPARATINGLINES": "Разделяющие линии",
    "CDLSHOOTINGSTAR": "Падающая звезда",
    "CDLSHORTLINE": "Короткая линия",
    "CDLSPINNINGTOP": "Вертящийся верх",
    "CDLSTALLEDPATTERN": "Застрявший паттерн",
    "CDLSTICKSANDWICH": "Палочки и бутерброд",
    "CDLTAKURI": "Такури",
    "CDLTASUKIGAP": "Гэп Тасуки",
    "CDLTHRUSTING": "Толкающий",
    "CDLTRISTAR": "Три звезды",
    "CDLUNIQUE3RIVER": "Уникальная тройная река",
    "CDLUPSIDEGAP2CROWS": "Пробел вверх у двух ворон",
    "CDLXSIDEGAP3METHODS": "Пробел по бокам от трех методов",
}





def fetch_cryptocurrency_data(crypto, interval):
    exchange = ccxt.binance()
    data = exchange.fetch_ohlcv(crypto, timeframe=interval, limit=100)
    
    ohlcv_data = {
        'timestamp': [datetime.fromtimestamp(candle[0] / 1000) for candle in data],
        'open': [candle[1] for candle in data],
        'high': [candle[2] for candle in data],
        'low': [candle[3] for candle in data],
        'close': [candle[4] for candle in data],
        'volume': [candle[5] for candle in data]
    }
    
    return ohlcv_data


def find_chart_patterns(crypto, interval):
    data = fetch_cryptocurrency_data(crypto, interval)
    ohlc_data = np.array([data['open'], data['high'], data['low'], data['close']]).T
    patterns = talib.get_function_groups()['Pattern Recognition']
    found_patterns = []
    
    for pattern in patterns:
        try:
            result = getattr(talib, pattern)(*ohlc_data.T)
            if result[-1] != 0:
                found_patterns.append(pattern)
        except TypeError as e:
            if "positional arguments (3 given)" in str(e):
                result = getattr(talib, pattern)(*ohlc_data.T[:-1]) 
                if result[-1] != 0:
                    found_patterns.append(pattern)
    
    found_patterns_names = [pattern_codes.get(pattern, pattern) for pattern in found_patterns]
    
    if found_patterns_names:
        return f"Найдены следующие паттерны на графике {interval} для {crypto}: {', '.join(found_patterns_names)}"
    else:
        return f"На графике {interval} для {crypto} не найдены паттерны"


def support_resistance_zones(crypto, interval):
    data = fetch_cryptocurrency_data(crypto, interval)
    low_prices = np.array(data['low'])
    high_prices = np.array(data['high'])
    support_level = talib.MIN(low_prices, timeperiod=30)[-1]
    resistance_level = talib.MAX(high_prices, timeperiod=30)[-1]
    return f"Зона поддержки: ${support_level:.2f} - ${support_level + 200:.2f}, Зона сопротивления: ${resistance_level:.2f} - ${resistance_level + 200:.2f}", support_level, resistance_level


def price_forecast(crypto, interval):
    data = fetch_cryptocurrency_data(crypto, interval)
    
    X = np.arange(len(data['close'])).reshape(-1, 1)
    y = data['close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model1 = GradientBoostingRegressor(n_estimators=200, random_state=42)
    model2 = RandomForestRegressor(n_estimators=200, random_state=42)
    model3 = LinearRegression()
    
    ensemble_model = VotingRegressor([('gb', model1), ('rf', model2), ('lr', model3)])
    
    ensemble_model.fit(X_train, y_train)
    
    y_pred = ensemble_model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    
    next_period = np.array([len(data['close'])]).reshape(-1, 1)
    next_price = ensemble_model.predict(next_period)
    # Среднеквадратичная ошибка: {mse:.2f}
    return f"Прогноз цены закрытия криптовалюты {crypto} на следующий период: ${next_price[0]:.2f}"


def fetch_current_price(crypto):
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(crypto)
        current_price = ticker['last']
        return current_price
    except ccxt.NetworkError as e:
        return f"Ошибка при получении текущей цены: {str(e)}"
    except ccxt.ExchangeError as e:
        return f"Ошибка при получении текущей цены: {str(e)}"
    except Exception as e:
        return f"Неизвестная ошибка: {str(e)}"


def generate_analysis_report(crypto, interval):
    try:
        current_price = fetch_current_price(crypto)
        if isinstance(current_price, str):
            return "Ошибка пара не найдена!", [], None, None
        
        patterns_message = find_chart_patterns(crypto, interval)
        support_resistance_message, support_level, resistance_level = support_resistance_zones(crypto, interval)
        forecast_message = price_forecast(crypto, interval)
        
        report = f"📈 Анализ графика криптовалюты {crypto} на интервале {interval}:\n\n"
        
        report += f"📊 Текущая цена криптовалюты {crypto}: ${current_price:.2f}\n\n"
        report += "🔍 Паттерны на графике:\n"
        report += patterns_message + "\n\n"
        report += "💪 Зоны поддержки и сопротивления:\n"
        report += support_resistance_message + "\n\n"
        report += "🔮 Прогноз цены на следующий период:\n"
        report += forecast_message
        if current_price < float(forecast_message.split(":")[1].split("$")[1].split(",")[0]):
            report += "💰 Рекомендация: Покупать"
        else:
            report += "💰 Рекомендация: Продавать"



        return report, support_level, resistance_level
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"


def generate_chart(crypto, interval, ohlcv_data, support_level, resistance_level):
    df = pd.DataFrame(ohlcv_data)
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
            
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    mpf.plot(df, type='candle', ax=ax[0], style='charles', volume=ax[1])

    ax[0].axhline(y=support_level, color='blue', linestyle='--', linewidth=1)
    ax[0].axhline(y=resistance_level, color='red', linestyle='--', linewidth=1)

    ax[0].set_title(f'{crypto} {interval} Chart')
    ax[0].set_ylabel('Price')
    ax[1].set_ylabel('Volume')

    chart_dir = os.path.join(os.getcwd(), "charts")
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, f"{crypto.replace('/', '_')}_{interval}.png")
    plt.savefig(chart_path)
    plt.close(fig) 

    return chart_path

