import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODELSLAB_API_KEY = os.getenv("MODELSLAB_API_KEY")  # Добавьте в .env

# ===== Gemini =====
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
                    "Добавь только лёгкие улучшения — уточни аниме-стиль, добавь светлый белый фон и простую магическую атмосферу "
                    "(например, лёгкую ауру или сияние), если это не противоречит описанию. "
                    "Избегай брони, крови и агрессии, если это явно не указано. "
                    "Добавь стиль рисовки 'anime flatter style'. "
                    "Размести персонажа по центру изображения. "
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
        parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        if parts and "text" in parts[0]:
            return parts[0]["text"].strip()
        print("Неверная структура ответа от Gemini:", result)
    except Exception as e:
        print("Ошибка Gemini:", e)
    return None

# ===== Modelslab API =====
def generate_image_with_modelslab(prompt):
    url = "https://modelslab.com/api/v6/images/text2img"
    headers = {
        "key": MODELSLAB_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "model_id": "boziorealvisxlv4",
        "lora_model": None,
        "width": "512",
        "height": "768",
        "negative_prompt": "(low quality, blurry, deformed, ugly, grainy, nsfw, text, signature, watermark)",
        "num_inference_steps": "30",
        "scheduler": "DPMSolverMultistepScheduler",
        "guidance_scale": "7.5",
        "enhance_prompt": None
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()

        output = result.get("output", [])
        if output:
            return output[0]

        # Если output пустой, пробуем fetch_result
        fetch_url = result.get("fetch_result")
        if fetch_url:
            print("Ожидаем генерацию изображения (fetch)...")
            time.sleep(2)  # подождём 2 секунды перед fetch

            for _ in range(5):  # максимум 5 попыток
                fetch_resp = requests.get(fetch_url, headers=headers)
                if fetch_resp.status_code == 200:
                    fetch_json = fetch_resp.json()
                    output = fetch_json.get("output", [])
                    if output:
                        return output[0]
                time.sleep(2)

            print("fetch_result вернул пустой output после повторных попыток")
        else:
            print("Отсутствует fetch_result в ответе")

    except Exception as e:
        print("Ошибка Modelslab:", e)

    return None


# ===== Flask route =====
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

    print("Шаг 2: Генерация изображения через Modelslab...")
    image_url = generate_image_with_modelslab(improved_prompt)
    if not image_url:
        return jsonify({"error": "Не удалось сгенерировать изображение"}), 500

    return jsonify({"url": image_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
