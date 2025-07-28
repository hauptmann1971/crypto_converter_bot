import requests
import json

crypto_id = 'cardano'
currency_code = 'usd'
response = {}
response_json = {}
try:
    header = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency_code}"
    response = requests.get(header)
    response_json = json.loads(response.text)
    print(response_json)
    print(response_json[crypto_id][currency_code])
except Exception as e:
    print(f"Возникла ошибка:{response} и {e}")