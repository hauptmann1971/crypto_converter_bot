# Программа "Конвертер криптовалют" для определения курса криптовалют к основным валютам

from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
from datetime import datetime
import requests
import json
from config import *
# import psycopg2
from Test_db_logger import create_table, insert_data


# Загрузка словаря криптовалют через API
def setup_cryptocurrencies() -> None:
    global response
    try:
        url: str = URL_COINS
        headers: dict = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        response_json: list = list(json.loads(response.text))
        crypto: list = []
        for x in response_json:
            ls: tuple = (x['id'], x['name'])
            crypto.append(ls)
        crypto_currencies.update(dict(crypto))
    except Exception:
        mb.showerror("Ошибка при загрузке списка актуальных криптовалют", f"Возникла ошибка: {response.status_code}")


# Получение id выбранной криптовалюты из Combobox
def get_crypto(event: Event) -> None:
    global crypto_id
    crypto_name: str = combo_crypto.get()
    for k, v in crypto_currencies.items():
        if v == crypto_name:
            crypto_id = k


# Получение кода выбранной валюты из Combobox
def get_currency(event: Event) -> None:
    global currency_name
    currency_name = combo_currency.get()


# Получение кода валюты по ее имени
def get_currency_code() -> str:
    for k, v in currencies.items():
        if v == currency_name:
            return k


# Получение json-словаря о курсе криптовалюты к валюте
def get_rate() -> dict:
    global response
    url: str = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={get_currency_code()}"
    response = requests.get(url)
    return json.loads(response.text)


# Извлечение данных о курсе криптовалюты к валюте из словаря и отбражение информации в метке
def show_rate() -> None:
    global response
    try:
        response = get_rate()
        crypto: str = ''
        currency: str = ''
        rate: float = 0.0
        for k, v in response.items():
            crypto = k
            if v == {}:
                mb.showerror("Ошибка!", "По этой криптовалюте нет информации о курсе")
                lbl.config(text="")
                return
            for i, j in v.items():
                currency = i
                rate = j
        lbl.config(text=f'Курс "{crypto.upper()}" к\n"{currencies[currency.upper()]}": {rate: .6f}')
        now = datetime.now()
        lbl_date.config(text=f"Дата/{now.day}/{now.month}/{now.year}  Время: {now.hour}:{now.minute}")
        if not insert_data(crypto_name=crypto, currency_name=currency, exchange_rate=rate, current_time=now):
            mb.showerror("Запись в базу данных", "Ошибка записи запроса в базу данных")
        else:
            mb.showinfo("Запись в базу данных", "Запись в базу данных произведена успешно")
    except Exception as e:
        mb.showerror("Ошибка", f"Возникла ошибка:{response} и {e}")
        lbl.config(text="")


# Словарь основных криптовалют
crypto_currencies: dict = CRYPTO_CURRENCIES

# Словарь основных валют
currencies: dict = CURRENCIES

# Глобальные переменные для формирования запросов к API
crypto_id = DEFAULT_CRYPTO
currency_name = DEFAULT_CURRENCY_NAME
response = None

# Вызов функции для обновления словаря актуальных криптовалют
setup_cryptocurrencies()  # setup_cryptocurrencies()

# Графический интерфейс с основным циклом программы
root = Tk()
root.title(MAIN_WINDOW_TITLE)
icon = PhotoImage(file=MAIN_WINDOW_TITLE_ICON)
root.iconphoto(False, icon)
root.geometry(MAIN_WINDOW_GEOMETRY)

combo_crypto_var = StringVar(value=DEFAULT_CRYPTO)
lbl_crypto = ttk.Label(text=CRYPTO_CURRENCY_LABEL_TEXT, font=DEFAULT_FONT)
lbl_crypto.pack(pady=10)
combo_crypto = ttk.Combobox(root, textvariable=combo_crypto_var, values=list(crypto_currencies.values()),
                            font=DEFAULT_FONT)

combo_crypto.pack(pady=10)
combo_crypto.bind("<<ComboboxSelected>>", get_crypto)

combo_currency_var = StringVar(value=DEFAULT_CURRENCY_NAME)
lbl_currency = ttk.Label(text=CURRENCY_LABEL_TEXT, font=DEFAULT_FONT)
lbl_currency.pack(pady=10)
combo_currency = ttk.Combobox(root, textvariable=combo_currency_var, values=list(currencies.values()),
                              font=DEFAULT_FONT)
combo_currency.pack(pady=10)
combo_currency.bind("<<ComboboxSelected>>", get_currency)

lbl = ttk.Label(root, font=DEFAULT_FONT)
lbl.pack(pady=10)

btn = Button(root, text=BUTTON_TEXT, font=DEFAULT_FONT, command=show_rate)
btn.pack(pady=10, anchor="s")

lbl_date = ttk.Label(root, font=DEFAULT_FONT)
lbl_date.pack(pady=10)

create_table()

root.mainloop()
