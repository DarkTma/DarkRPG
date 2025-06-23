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
AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY")  # Этот ключ больше не используется
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ключ для Gemini API


def call_gemini_text_api(user_prompt):
    """
    Отправляем запрос к Gemini API (текстовой модели) для перевода и улучшения промта.
    Возвращаем улучшенный англоязычный prompt в виде чистого текста.
    """
    # Актуальный URL для Gemini API (используем gemini-1.5-flash для текстовых задач)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    # Формируем системное и пользовательское сообщения для Gemini
    # Добавлено четкое указание НЕ использовать Markdown и форматирование
    messages = [
        {
            "role": "user",
            "parts": [
                {"text": (
                    "Ты — помощник, который переводит текст с русского на английский "
                    "и улучшает его для генерации аниме-персонажа. "
                    "Переведи и сделай промт максимально детализированным и подходящим для AI генерации. "
                    "Ответь только улучшенным промтом, без каких-либо дополнительных слов, заголовков, "
                    "маркированных списков или форматирования Markdown. Просто сгенерированный текст."
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
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Проверяем структуру ответа перед извлечением
        if result and "candidates" in result and len(result["candidates"]) > 0 and \
                "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"] and \
                len(result["candidates"][0]["content"]["parts"]) > 0 and \
                "text" in result["candidates"][0]["content"]["parts"][0]:
            improved_prompt = result["candidates"][0]["content"]["parts"][0]["text"]
            return improved_prompt.strip()
        else:
            print(f"Ошибка парсинга ответа Gemini (текст): Неожиданная структура. Ответ: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP-запроса к Gemini (текст): {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка Gemini API (текст): {e}. Ответ: {getattr(response, 'text', 'Нет ответа')}")
        return None


def call_gemini_image_api(image_prompt):
    """
    Отправляем запрос к Gemini API (модель для генерации изображений) для создания аниме-изображения.
    Возвращаем URL с base64 изображением.
    """
    # URL для модели Imagen 3 (для генерации изображений)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "instances": {
            "prompt": image_prompt  # Используем улучшенный промт для генерации изображения
        },
        "parameters": {
            "sampleCount": 1  # Генерируем одно изображение
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        if result and "predictions" in result and len(result["predictions"]) > 0:
            base64_image = result["predictions"][0]["bytesBase64Encoded"]
            image_url = f"data:image/png;base64,{base64_image}"
            return image_url
        else:
            print(f"Gemini (изображение) не вернул изображение или ответ пуст. Ответ: {result}")
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

    print("Шаг 1: Улучшаем промт с помощью текстовой модели Gemini...")
    improved_prompt = call_gemini_text_api(prompt)
    if not improved_prompt:
        return jsonify({"error": "Failed to improve prompt with Gemini API"}), 500

    print(f"Полученный от Gemini улучшенный prompt (чистый текст):\n{improved_prompt}")

    print("Шаг 2: Начинаем генерацию изображения с Gemini...")
    image_url = call_gemini_image_api(improved_prompt)
    if not image_url:
        return jsonify({"error": "Failed to generate image with Gemini API"}), 500

    print("Изображение успешно сгенерировано.")
    return jsonify({"url": image_url})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
