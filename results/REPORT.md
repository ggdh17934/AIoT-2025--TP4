# TP4 report

Both TP2 pipelines load successfully with all 12 sensor fields in the original
order. The first dataset reading produces LR probability
0.999977 and XGBoost probability
0.000340. Both models are evaluated;
the selected CLI model controls the returned decision. Actual pipeline file sizes:
LR 1.642 KB;
XGB 120.317 KB.

The real Flask endpoint was exercised in-process: valid request HTTP 200,
missing sensor fields HTTP 400. The local request round trip was
7.219 ms. This is a **host/in-process** measurement, not WiFi/MQTT
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
