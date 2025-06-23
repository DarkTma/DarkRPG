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
                    "Избегай брони, крови и агрессии, если это явно не указано. "
                    "Укажи стиль рисовки, например 'anime flatter style'. "
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
        print(f"\u041e\u0448\u0438\u0431\u043a\u0430 Gemini: {e}")
        return None

def generate_image_with_replicate(prompt):
    try:
        output = replicate.run(
            "flat-2d-animerge",  # Здесь можно заменить модель
            input={
                "prompt": prompt,
                "width": 512,
                "height": 512,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )
        if output:
            return str(output[0])
        return None
    except Exception as e:
        print(f"\u041e\u0448\u0438\u0431\u043a\u0430 Replicate: {e}")
        return None

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    print("\u0428\u0430\u0433 1: \u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043f\u0440\u043e\u043c\u0442\u0430 \u0447\u0435\u0440\u0435\u0437 Gemini...")
    improved_prompt = call_gemini_text_api(prompt)
    if not improved_prompt:
        return jsonify({"error": "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0443\u043b\u0443\u0447\u0448\u0438\u0442\u044c \u043f\u0440\u043e\u043c\u0442 \u0447\u0435\u0440\u0435\u0437 Gemini"}), 500

    print(f"\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u044b\u0439 \u043f\u0440\u043e\u043c\u0442: {improved_prompt}")

    print("\u0428\u0430\u0433 2: \u0413\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u0447\u0435\u0440\u0435\u0437 Replicate...")
    image_url = generate_image_with_replicate(improved_prompt)
    if not image_url:
        return jsonify({"error": "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0447\u0435\u0440\u0435\u0437 Replicate"}), 500

    return jsonify({"url": image_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
