import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json  # для красивого вывода JSON
from dotenv import load_dotenv  # ← добавляем

load_dotenv()


app = Flask(__name__)
CORS(app)

# Подставьте свой API-ключ от AI Horde
AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    headers = {
        "apikey": AI_HORDE_API_KEY,
        "Client-Agent": "DarkRPGApp:1.0:telegram.com/darktma"
    }

    payload = {
        "prompt": prompt,
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

    # Логируем отправляемый payload
    print("Отправляемый JSON payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("AI_HORDE_API_KEY =", os.getenv("AI_HORDE_API_KEY"))

    try:
        # Отправляем задачу на генерацию
        r = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers=headers)
        print("Ответ status code:", r.status_code)
        print("Ответ body:", r.text)  # тело ответа в строковом формате
        r.raise_for_status()
        task_id = r.json()["id"]

        # Ожидаем результат
        while True:
            check_response = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", headers=headers)
            check = check_response.json()
            print("Статус задачи:", json.dumps(check, indent=2, ensure_ascii=False))
            if check.get("done"):
                image_url = check["generations"][0]["img"]
                return jsonify({"url": image_url})
            if check.get("message") == "10 per 1 minute":
                time.sleep(10)
                continue
            time.sleep(6)
    except Exception as e:
        print("Ошибка:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
