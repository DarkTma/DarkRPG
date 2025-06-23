import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

app = Flask(__name__)
# Включаем CORS для разрешения кросс-доменных запросов
CORS(app)

# Получаем ключи API из переменных окружения
AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY") # Возможно, этот ключ больше не понадобится, но оставим его
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ключ для Gemini API

def call_gemini_text_api(user_prompt):
    """
    Отправляем запрос к Gemini API (текстовой модели) для перевода и улучшения промта.
    Возвращаем улучшенный англоязычный prompt.
    """
    # Актуальный URL для Gemini API (используем gemini-1.5-flash для текстовых задач)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    # Формируем системное и пользовательское сообщения для Gemini
    # Gemini API использует формат 'parts' для контента
    messages = [
        {
            "role": "user",
            "parts": [
                {"text": (
                    "Ты — помощник, который переводит текст с русского на английский "
                    "и улучшает его для генерации аниме-персонажа. "
                    "Переведи и сделай промт максимально детализированным и подходящим для AI генерации. "
                    "Укажи стиль 'аниме'."
                )},
                {"text": user_prompt}
            ]
        }
    ]
    data = {
        "contents": messages,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30) # Добавляем таймаут
        response.raise_for_status() # Вызывает исключение для плохих ответов (4xx или 5xx)
        result = response.json()
        # Извлекаем текст из ответа Gemini
        improved_prompt = result["candidates"][0]["content"]["parts"][0]["text"]
        return improved_prompt.strip()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP-запроса к Gemini (текст): {e}")
        return None
    except KeyError as e:
        print(f"Ошибка парсинга ответа Gemini (текст): Не найден ключ {e}. Ответ: {result}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка Gemini API (текст): {e}")
        return None

def call_gemini_image_api(image_prompt):
    """
    Отправляем запрос к Gemini API (модель для генерации изображений) для создания аниме-изображения.
    Возвращаем URL с base64 изображением.
    """
    # URL для модели Imagen 3 (для генерации изображений)
    # Используем imagen-3.0-generate-002, так как это специализированная модель для генерации изображений
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "instances": {
            "prompt": image_prompt # Используем улучшенный промт для генерации изображения
        },
        "parameters": {
            "sampleCount": 1 # Генерируем одно изображение
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60) # Увеличиваем таймаут для генерации изображений
        response.raise_for_status() # Вызывает исключение для плохих ответов
        result = response.json()

        # Проверяем, что ответ содержит сгенерированные изображения
        if result and "predictions" in result and len(result["predictions"]) > 0:
            # Изображение возвращается в base64
            base64_image = result["predictions"][0]["bytesBase64Encoded"]
            # Формируем data URL для изображения
            image_url = f"data:image/png;base64,{base64_image}"
            return image_url
        else:
            print(f"Gemini (изображение) не вернул изображение. Ответ: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP-запроса к Gemini (изображение): {e}")
        return None
    except KeyError as e:
        print(f"Ошибка парсинга ответа Gemini (изображение): Не найден ключ {e}. Ответ: {result}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка Gemini API (изображение): {e}")
        return None

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Шаг 1: Улучшаем промт с помощью текстовой модели Gemini
    improved_prompt = call_gemini_text_api(prompt)
    if not improved_prompt:
        return jsonify({"error": "Failed to improve prompt with Gemini API"}), 500

    print(f"Полученный от Gemini улучшенный prompt:\n{improved_prompt}")

    # Шаг 2: Генерируем изображение с помощью модели Gemini для изображений
    print("Начинаем генерацию изображения с Gemini...")
    image_url = call_gemini_image_api(improved_prompt)
    if not image_url:
        return jsonify({"error": "Failed to generate image with Gemini API"}), 500

    print("Изображение успешно сгенерировано.")
    # Возвращаем URL с base64 изображением
    return jsonify({"url": image_url})

if __name__ == "__main__":
    # Запускаем Flask приложение на всех доступных интерфейсах по порту 5000
    app.run(host="0.0.0.0", port=5000)

