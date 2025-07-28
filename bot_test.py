from flask import Flask, request, jsonify
import telebot
from telebot import types
import logging


# Настройки
TOKEN = "8162915842:AAGI51F4JzqFsq5g6T6UI9nt8dNH82oWRKY"  # Замените на токен от @BotFather
PORT = 5000

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Временное хранилище данных пользователей
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Инициализируем хранилище для пользователя
    bot.send_message(chat_id, "Привет! Я бот-калькулятор. 🧮\nВведи первое число:")
    bot.register_next_step_handler(message, get_first_number)

# Получение первого числа
def get_first_number(message):
    chat_id = message.chat.id
    try:
        num1 = float(message.text)
        user_data[chat_id]['num1'] = num1
        bot.send_message(chat_id, "Отлично! Теперь введи второе число:")
        bot.register_next_step_handler(message, get_second_number)
    except ValueError:
        bot.send_message(chat_id, "Ошибка! Это не число. Попробуй еще раз:")
        bot.register_next_step_handler(message, get_first_number)

# Получение второго числа и вывод результата
def get_second_number(message):
    chat_id = message.chat.id
    try:
        num2 = float(message.text)
        num1 = user_data[chat_id]['num1']
        
        # Вычисляем сумму и произведение
        sum_result = num1 + num2
        product_result = num1 * num2
        
        bot.send_message(
            chat_id,
            f"🔢 Результаты:\n"
            f"Сумма: {num1} + {num2} = {sum_result}\n"
            f"Произведение: {num1} * {num2} = {product_result}"
        )
        del user_data[chat_id]  # Очищаем данные
    except ValueError:
        bot.send_message(chat_id, "Ошибка! Это не число. Попробуй еще раз:")
        bot.register_next_step_handler(message, get_second_number)

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
    url_tunnel = 'https://9279c9d7-b4e2-46e1-917e-8bd5cd9facef.tunnel4.com'
    webhook_url = f"{url_tunnel}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")
    return f"Webhook настроен! URL: {webhook_url}"

if __name__ == '__main__':
    app.run(port=PORT)
