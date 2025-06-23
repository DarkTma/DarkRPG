import os
import replicate
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def call_gemini_text_api(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    messages = [
        {
            "role": "user",
            "parts": [
                {"text": (
                    "Ты — помощник, который переводит текст с русского на английский и немного улучшает его для генерации аниме-персонажа. "
                    "Сохрани все основные черты и настроение, заданные пользователем. "
                    "Добавь только лёгкие улучшения — уточни аниме-стиль, добавь светлый белый фон и простую магическую атмосферу (например, лёгкую ауру или сияние), если это не противоречит описанию. "
                    "Не делай описание перегруженным или слишком сложным. "
                    "Избегай брони, крови и агрессии, если это явно не указано. "
                    "Ответь только улучшенным текстом на английском, без форматирования или пояснений."
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

        if result and "candidates" in result and len(result["candidates"]) > 0:
            parts = result["candidates"][0]["content"]["parts"]
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()

        print("Неверная структура ответа от Gemini:", result)
        return None

    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        return None

def generate_image_with_replicate(prompt):
    try:
        output = replicate.run(
            "stability-ai/stable-diffusion-3.5-medium",
            input={"prompt": prompt}
        )
        if output:
            # Репликейт иногда возвращает список с URL-строкой или FileOutput объектом — приводим к строке
            first_item = output[0]
            return str(first_item)  # Явно превращаем в строку
        return None
    except Exception as e:
        print(f"Ошибка Replicate: {e}")
        return None


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    print("Шаг 1: Обработка промта через Gemini...")
    improved_prompt = call_gemini_text_api(prompt)
    if not improved_prompt:
        return jsonify({"error": "Не удалось улучшить промт через Gemini"}), 500

    print(f"Улучшенный промт: {improved_prompt}")

    print("Шаг 2: Генерация изображения через Replicate...")
    image_url = generate_image_with_replicate(improved_prompt)
    if not image_url:
        return jsonify({"error": "Не удалось сгенерировать изображение через Replicate"}), 500

    return jsonify({"url": image_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
