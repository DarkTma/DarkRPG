import os
from dotenv import load_dotenv
import replicate
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()  # загружаем переменные из .env

app = Flask(__name__)
CORS(app)

# Получаем токен из переменной окружения
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    try:
        output = replicate.run(
            "stability-ai/stable-diffusion-3.5-medium",
            input={"prompt": prompt}
        )
        return jsonify({"url": output[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
