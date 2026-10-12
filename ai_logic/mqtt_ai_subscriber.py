"""Run: python -m ai_logic.mqtt_ai_subscriber --model lr --broker localhost."""
import argparse
import json
import logging
import os

import paho.mqtt.client as mqtt
from ai_logic.inference import infer, load_models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["lr", "xgb"], default="lr")
    parser.add_argument("--broker", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--tls", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    load_models()

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            logging.error("Connection rejected: %s", reason_code)
            return
        client.subscribe("esp32/data", qos=1)
        logging.info("Connected; subscribed to esp32/data")

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload)
            response = infer(payload, args.model)
            client.publish("esp32/control", json.dumps(response), qos=1, retain=False)
            logging.info("%s", response)
        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as error:
            logging.warning("Ignored malformed message: %s", error)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ghanabzia-tp4-ai")
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    if args.tls:
        client.tls_set()
    username = os.environ.get("MQTT_USERNAME")
    if username:
        client.username_pw_set(username, os.environ.get("MQTT_PASSWORD"))
    client.connect_async(args.broker, args.port, keepalive=30)
    try:
        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        client.disconnect()


if __name__ == "__main__":
    main()
