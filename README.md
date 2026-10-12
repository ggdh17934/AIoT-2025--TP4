# AIoT-2025--TP4 — MQTT and HTTP inference

Simple, documented solution to [the course TP4](https://github.com/ahmed3991/AIoT-2025/tree/main/TP4).

[Open notebook in Colab](https://colab.research.google.com/github/ggdh17934/AIoT-2025--TP4/blob/main/TP4-Ghanabzia.ipynb)

This repository is **private**. Sign in with your GitHub account when Colab asks
for access. You can also download the notebook and use Colab's **Upload** option.

## Run locally

Use Python 3.11 or newer (TensorFlow builds depend on the supported Python version).
From this project folder:

```sh
python -m pip install -r requirements.txt
python tp4.py
```

## Run the notebook

Run all and upload the included models/LR-Pipeline.pkl and XGB-Pipeline.pkl when prompted. Supporting Python modules are recreated by the notebook. The local demo runs in Colab; a network subscriber should run on your computer next to a reachable broker.

The first notebook cell installs missing dependencies. TP2/TP4 also ensure the
versions used for their pickle models. All notebooks contain the actual solution
code; they do not require downloading the Python script just to execute cells.
Saved outputs come from the local run; rerunning generates your own measurements.

## Files

- `TP4-Ghanabzia.ipynb`: notebook with code, outputs, and report display.
- `tp4.py`: Python solution.
- `EXPLICATION_AR.md`: Arabic explanation of the code, concepts and limitations.
- `results/REPORT.md`: measured results and conclusions.
- `results/VALIDATION.md`: what was actually checked.
- `requirements.txt`: runtime dependencies.

## Embedded part

The notebook demonstrates the host-side work. The assignment also requires
`src/main.cpp`, `platformio.ini`, and `diagram.json` for the board/simulator.
Install PlatformIO, open this folder and build:

```sh
pio run -e esp32dev
```

Run the included Wokwi project from VS Code, or upload the sketch to the matching
board. No hardware measurements are invented; see `results/VALIDATION.md` and
GitHub Actions for the actual build status.


## Network modes

Run the subscriber in a separate local terminal with a reachable broker:

```sh
python -m ai_logic.mqtt_ai_subscriber --model lr --broker localhost
python -m ai_logic.http_server
```

For the public classroom Wokwi default, pass `--broker broker.mqtt.cool` to Python.
The default ESP32 sketch simulates ten sensor readings and reads only the two DHT
values; do not interpret the replay constants as real connected sensors.
Use `pio run -e esp32-http` for the HTTP firmware alternative. For LAN HTTP,
set `HTTP_HOST=0.0.0.0` before starting Python and set `HTTP_URL` to your host's
reachable address. Wokwi's host.wokwi.internal needs its local gateway support.
For configured authenticated brokers, Python accepts `--tls --port 8883` and
`MQTT_USERNAME`/`MQTT_PASSWORD` environment variables. No credentials are committed.

## Sources and attribution

Assignment and original wiring: Ahmed Ghenabzia,
[ahmed3991/AIoT-2025](https://github.com/ahmed3991/AIoT-2025).
Solution Python and firmware are implemented for this project; diagrams are
adapted from the course starter files. Smoke data source:
[Kaggle Smoke Detection](https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset).
Fashion-MNIST is loaded through the official Keras dataset loader; source:
[Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist).
