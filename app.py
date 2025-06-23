import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def call_gemini_text_api(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    messages = [
        {
            "role": "user",
            "parts": [
                {"text": (
                    "Ты — помощник, который переводит текст с русского на английский "
                    "и улучшает его для генерации аниме-персонажа. "
                    "Переведи и сделай промт максимально детализированным и подходящим для AI генерации. "
                    "Ответь только улучшенным промтом, без форматирования Markdown или пояснений."
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
        parts = result["candidates"][0]["content"]["parts"]
        return parts[0]["text"].strip()
    except Exception as e:
        print("Ошибка Gemini API:", str(e))
        return None


def generate_image_with_horde(prompt):
    headers = {
        "apikey": AI_HORDE_API_KEY,
        "Client-Agent": "DarkRPGApp:1.0:telegram.com/darktma"
    }

    payload = {
        "prompt": prompt,
        "models": ["anything-v5"],
        "params": {
            "n": 1,
            "width": 512,
            "height": 512,
            "karras": True,
            "sampler_name": "k_euler",
            "steps": 25,
            "cfg_scale": 7.0,
            "trusted_workers": True
        }
    }

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers=headers)
        r.raise_for_status()
        task_id = r.json()["id"]

        while True:
            check_response = requests.get(
                f"https://stablehorde.net/api/v2/generate/status/{task_id}", headers=headers)
            check = check_response.json()
            if check.get("done"):
                image_url = check["generations"][0]["img"]
                return image_url
            if check.get("message") == "10 per 1 minute":
                time.sleep(10)
            else:
                time.sleep(6)
    except Exception as e:
        print("Ошибка генерации изображения через AI Horde:", str(e))
        return None


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    print("Шаг 1: Перевод и улучшение промта через Gemini...")
    improved_prompt = call_gemini_text_api(prompt)
    if not improved_prompt:
        return jsonify({"error": "Gemini не смог улучшить промт"}), 500

    print(f"Улучшенный prompt:\n{improved_prompt}")

    print("Шаг 2: Генерация изображения через AI Horde...")
    image_url = generate_image_with_horde(improved_prompt)
    if not image_url:
        return jsonify({"error": "Не удалось сгенерировать изображение через AI Horde"}), 500

    return jsonify({"url": image_url})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
