"""TP4 notebook/local demo: real inference and HTTP without a broker or board."""
# %% 1. Imports and models
import json
from pathlib import Path
from time import perf_counter

from ai_logic.inference import FEATURES, infer, load_models
from ai_logic.http_server import app

ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
load_models()

# %% 2. A valid payload containing all twelve actual TP2 sensor fields
# Replay the first real CSV reading; this is a host demonstration, not a live sensor.
payload = {
    "device_id": "esp-01", "request_id": 1, "timestamp": 0,
    "readings": dict(zip(FEATURES, [20.0, 57.36, 0, 400, 12306, 18520,
                                  939.735, 0, 0, 0, 0, 0])),
}
(ROOT / "sample_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
response = infer(payload, selected="lr")
print("Input:\n", json.dumps(payload, indent=2))
print("Both model predictions:\n", json.dumps(response, indent=2))

# %% 3. Exercise the real POST endpoint and reject malformed sensor payloads
with app.test_client() as client:
    start = perf_counter()
    http_response = client.post("/infer?model=xgb", json=payload)
    http_local_ms = (perf_counter() - start) * 1000
    assert http_response.status_code == 200
    assert http_response.get_json()["model"] == "xgb"
    assert http_response.get_json()["prediction"] == response["both_models"]["xgb"]["prediction"]
    invalid = client.post("/infer", json={"device_id": "esp-01", "readings": {}})
    assert invalid.status_code == 400
    print("HTTP valid status:", http_response.status_code)
    print("HTTP malformed status:", invalid.status_code)
    print("Local in-process HTTP round trip (ms):", http_local_ms)

# %% 4. Report and how to run the two network services
(OUT / "demo_response.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
report = f"""# TP4 report

Both TP2 pipelines load successfully with all 12 sensor fields in the original
order. The first dataset reading produces LR probability
{response['both_models']['lr']['probability']:.6f} and XGBoost probability
{response['both_models']['xgb']['probability']:.6f}. Both models are evaluated;
the selected CLI model controls the returned decision. Actual pipeline file sizes:
LR {(ROOT/'models'/'LR-Pipeline.pkl').stat().st_size / 1024:.3f} KB;
XGB {(ROOT/'models'/'XGB-Pipeline.pkl').stat().st_size / 1024:.3f} KB.

The real Flask endpoint was exercised in-process: valid request HTTP 200,
missing sensor fields HTTP 400. The local request round trip was
{http_local_ms:.3f} ms. This is a **host/in-process** measurement, not WiFi/MQTT
or ESP32 end-to-end latency. Firmware echoes request IDs and measures millis()
from publish to response on the same board, avoiding unsynchronized clock subtraction.
No board/network latency is invented.

MQTT: ESP32 -> esp32/data -> Python -> esp32/control -> ESP32 LED.
The subscriber uses QoS 1 for subscribe/reply, reconnect delay 1–30 seconds,
device IDs, finite-number validation and logging. The ESP32 PubSubClient
publisher sends QoS 0 (a library limitation); the JSON includes a request ID so
replies can be matched. QoS 1 can deliver duplicates; repeating LED state is
idempotent. The minimal classroom setup uses a local broker. Python supports
TLS and environment-based username/password for a configured authenticated broker.

HTTP: ESP32 POST /infer -> Python inference -> JSON HTTP response -> LED.
MQTT decouples producers/consumers and supports multiple subscribers, while HTTP
is simple request/response with larger header overhead. CoAP uses a lightweight
REST-style UDP transport; WebSockets provide persistent bidirectional communication.
The default firmware reads DHT22 temperature/humidity and replays fixed demo
values for the other ten sensors. Those constants are explicitly a classroom
simulation; actual deployment must connect all expected sensors or retrain a
two-feature pipeline. It never silently substitutes zeros for missing JSON fields.

Use a locally reachable broker, or the documented public demonstration mode.
For real hardware set WiFi settings and the host's LAN address; for a local
HTTP server accessible on LAN set HTTP_HOST=0.0.0.0. Colab can demonstrate
inference and the endpoint, but it is not a directly reachable local LAN broker.

Source: https://github.com/ahmed3991/AIoT-2025/blob/main/TP4/TP4.md
"""
(OUT / "REPORT.md").write_text(report, encoding="utf-8")
print("Saved results. Network commands (run in separate terminals):")
print("python -m ai_logic.mqtt_ai_subscriber --model lr --broker localhost")
print("python -m ai_logic.http_server")
