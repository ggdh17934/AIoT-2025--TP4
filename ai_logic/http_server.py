"""HTTP alternative: python -m ai_logic.http_server"""
import os
from flask import Flask, jsonify, request
from ai_logic.inference import infer

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.post("/infer")
def inference_endpoint():
    try:
        payload = request.get_json(silent=True)
        selected = request.args.get("model", "lr")
        return jsonify(infer(payload, selected))
    except (ValueError, TypeError, KeyError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host=os.environ.get("HTTP_HOST", "127.0.0.1"), port=5000, debug=False)
