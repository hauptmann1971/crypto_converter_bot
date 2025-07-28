from flask import Flask, request, jsonify
import telebot
import logging
import requests
import json
import coloredlogs

# Настройки
TOKEN = "8264247176:AAFByVrbcY8K-aanicYu2QK-tYRaFNq0lxY"
PORT = 5000
TUNNEL_URL = 'https://5c86f6cf-9300-44ea-aebf-3f3293066334.tunnel4.com'
CRYPTO_CURRENCY = {'bitcoin', 'ethereum', 'cardano'}
CURRENCY = {'usd', 'eur', 'rub', 'gbp'}


app = Flask(__name__)
bot = telebot.TeleBot(TOKEN, colorful_logs=True)

# Логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Временное хранилище данных пользователей
user_data = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Инициализируем хранилище для пользователя
    bot.send_message(chat_id, "Привет! Введи криптовалюту bitcoin, ethereum, cardano: ")
    bot.register_next_step_handler(message, get_crypto)


# Получение криптовалюты
def get_crypto(message):
    chat_id = message.chat.id
    crypto_id = str(message.text)
    if crypto_id in CRYPTO_CURRENCY:
        user_data[chat_id]['crypto_id'] = crypto_id
        bot.send_message(chat_id, "Отлично! Теперь введи название валюты usd, eur, rub, gbp: ")
        bot.register_next_step_handler(message, get_currency)
    else:
        bot.send_message(chat_id, "Ошибка! Неверное название криптовалюты. Попробуй еще раз и введи bitcoin, ethereum, cardano: ")
        bot.register_next_step_handler(message, get_crypto)


# Получение валюты, запрос  и вывод курса
def get_currency(message):
    chat_id = message.chat.id
    currency_code = str(message.text)
    response = {}
    response_json = {}
    if currency_code in CURRENCY:
        crypto_id = user_data[chat_id]['crypto_id']

    # Запрашиваем курс криптовалюты к фиатной валюте через  https://api.coingecko.com/api/:
        try:    # Проверяем успешность запроса к удаленному серверу:
            header = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency_code}"
            response = requests.get(header)
            response_json = json.loads(response.text)
        except Exception as e:
            bot.send_message(chat_id, f"Возникла ошибка:{response} и {e}")

        bot.send_message(   #Если запрос успешен, то обрабатываем полученный от сервера json и высылаем курс в ответном сообщении от бота:
            chat_id, f"🔢 Курс {crypto_id}/{currency_code} = {response_json[crypto_id][currency_code]}")
        del user_data[chat_id]  # Очищаем данные
    else:
        bot.send_message(chat_id, "Ошибка! Неверное название валюты. Попробуй еще раз и введи usd, eur, rub, gbp: ")
        bot.register_next_step_handler(message, get_currency)

# Тест вервера flask
@app.route("/")
def home():
    return "Сервер работает штатно!!!"


# Вебхук для Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "bad request"}), 400


# Установка вебхука
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = TUNNEL_URL
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Webhook установлен: {webhook_url}"


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
