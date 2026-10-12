# Validation

- All 7 notebook code cells executed successfully; genuine outputs are saved.
- Notebook format validated with nbformat.
- Python solution/support modules pass syntax compilation.
- Report and Arabic explanation are included.
- Actual subscriber passed a real localhost MQTT round trip via AMQTT: 7.683 ms.
- Temporary broker and clients were stopped after testing.
- This host MQTT result excludes ESP32/WiFi latency.
- GitHub Actions builds the ESP32 firmware on push; local toolchain unpacking exceeded available disk space and task-only downloads were removed.
- Real Flask POST /infer returned 200 for valid input and 400 for missing sensors.
- Both TP2 model results are included; model selection is exercised.
- No real-board runtime measurements or Wokwi observations are claimed.

## GitHub firmware build

**PASSED**: [Build run](https://github.com/ggdh17934/AIoT-2025--TP4/actions/runs/38261392155).

Both `esp32dev` (MQTT) and `esp32-http` firmware environments compiled successfully.
This proves compilation; board execution, sensor/LCD behavior and runtime timing remain separate observations.
