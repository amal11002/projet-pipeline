import json
import time
import requests
from kafka import KafkaProducer
import os
from dotenv import load_dotenv
load_dotenv()


KAFKA_BROKER = '127.0.0.1:9092'
API_KEY = os.getenv('API_KEY')
CITIES = ['Montreal', 'Quebec City', 'Toronto']
TOPIC = 'weather_data'

def get_weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(url, params=params)
    data = response.json()
    # print(f"Réponse API pour {city} : {data}")  # debug
    return {
        'city': city,
        'temp': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'wind': data['wind']['speed'],
        'description': data['weather'][0]['description'],
        'timestamp': time.time()
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(f"Producteur démarré — envoi vers le topic '{TOPIC}' toutes les 30s")

    while True:
        for city in CITIES:
            try:
                weather = get_weather(city)
                producer.send(TOPIC, weather)
                producer.flush()
                print(f"Envoyé : {weather}")
            except Exception as e:
                print(f"Erreur pour {city} : {e}")
        time.sleep(30)

if __name__ == '__main__':
    main()