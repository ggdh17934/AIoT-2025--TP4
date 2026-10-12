// TP4: DHT22 + demonstration readings -> MQTT/HTTP -> Python -> LED.
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#ifndef USE_HTTP
#define USE_HTTP 0
#endif

// Wokwi defaults. For hardware use your own WiFi and reachable LAN server.
const char *WIFI_SSID = "Wokwi-GUEST";
const char *WIFI_PASSWORD = "";
const char *MQTT_HOST = "broker.mqtt.cool"; // public classroom demonstration only
const char *HTTP_URL = "http://host.wokwi.internal:5000/infer?model=lr";
const int LED_PIN = 2;
const int DHT_PIN = 15;
DHT dht(DHT_PIN, DHT22);
WiFiClient network;
PubSubClient mqtt(network);
String deviceId;
unsigned long lastSend = 0;
unsigned long sentAt = 0;
unsigned long requestId = 0;
unsigned long lastReconnect = 0;
unsigned long reconnectDelay = 1000;

void applyResponse(const String &text) {
  JsonDocument response;
  if (deserializeJson(response, text)) return;
  if (String(response["device_id"].as<const char *>()) != deviceId) return;
  if (response["request_id"].as<unsigned long>() != requestId) return;
  digitalWrite(LED_PIN, response["prediction"].as<int>() == 1 ? HIGH : LOW);
  Serial.print("Prediction: "); Serial.println(response["prediction"].as<int>());
  Serial.print("Round-trip latency ms: "); Serial.println(millis() - sentAt);
}

void onMessage(char *topic, byte *payload, unsigned int length) {
  String text;
  text.reserve(length);
  for (unsigned int i = 0; i < length; ++i) text += char(payload[i]);
  applyResponse(text);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  dht.begin();
  deviceId = "ghanabzia-tp4-" + String(uint32_t(ESP.getEfuseMac()), HEX);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  mqtt.setServer(MQTT_HOST, 1883);
  mqtt.setCallback(onMessage);
  mqtt.setBufferSize(2048);
  mqtt.setSocketTimeout(2);
  Serial.println(deviceId);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  if (!USE_HTTP) {
    if (!mqtt.connected()) {
      if (millis() - lastReconnect < reconnectDelay) return;
      lastReconnect = millis();
      if (mqtt.connect(deviceId.c_str())) {
        mqtt.subscribe("esp32/control", 1);
        reconnectDelay = 1000;
      } else {
        reconnectDelay = min(reconnectDelay * 2, 30000UL);
        return;
      }
    }
    mqtt.loop();
  }
  if (millis() - lastSend < 3000) return;
  lastSend = millis();
  const float temperature = dht.readTemperature();
  const float humidity = dht.readHumidity();
  if (isnan(temperature) || isnan(humidity)) return;
  JsonDocument request;
  requestId = millis();
  request["device_id"] = deviceId;
  request["request_id"] = requestId;
  request["timestamp"] = millis() / 1000.0; // device uptime, not a UTC clock
  JsonObject readings = request["readings"].to<JsonObject>();
  readings["Temperature[C]"] = temperature;
  readings["Humidity[%]"] = humidity;
  // These ten fixed readings are a replay demonstration, not physical sensors.
  readings["TVOC[ppb]"] = 0;
  readings["eCO2[ppm]"] = 400;
  readings["Raw H2"] = 12306;
  readings["Raw Ethanol"] = 18520;
  readings["Pressure[hPa]"] = 939.735;
  readings["PM1.0"] = 0; readings["PM2.5"] = 0;
  readings["NC0.5"] = 0; readings["NC1.0"] = 0; readings["NC2.5"] = 0;
  String payload;
  serializeJson(request, payload);
  sentAt = millis();
  if (USE_HTTP) {
    HTTPClient http;
    http.setTimeout(5000);
    http.begin(HTTP_URL);
    http.addHeader("Content-Type", "application/json");
    const int status = http.POST(payload);
    if (status == 200) applyResponse(http.getString());
    else Serial.printf("HTTP status: %d\n", status);
    http.end();
  } else if (!mqtt.publish("esp32/data", payload.c_str())) {
    Serial.println("Publish failed");
  }
}
