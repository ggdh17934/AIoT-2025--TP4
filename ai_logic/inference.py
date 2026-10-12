"""Shared prediction code for MQTT, HTTP, and the notebook demo."""
import math
import pickle
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["Temperature[C]", "Humidity[%]", "TVOC[ppb]", "eCO2[ppm]",
            "Raw H2", "Raw Ethanol", "Pressure[hPa]", "PM1.0", "PM2.5",
            "NC0.5", "NC1.0", "NC2.5"]
PIPELINES = {}


def load_models():
    if PIPELINES:
        return PIPELINES
    missing = [f"{name}-Pipeline.pkl" for name in ["LR", "XGB"]
               if not (ROOT / "models" / f"{name}-Pipeline.pkl").exists()]
    if missing:
        try:
            from google.colab import files
        except ImportError as error:
            raise FileNotFoundError("Copy both TP2 pipeline files into models/.") from error
        print("Upload TP2's LR-Pipeline.pkl and XGB-Pipeline.pkl")
        (ROOT / "models").mkdir(exist_ok=True)
        for name, content in files.upload().items():
            if Path(name).name in ["LR-Pipeline.pkl", "XGB-Pipeline.pkl"]:
                (ROOT / "models" / Path(name).name).write_bytes(content)
    for name, prefix in [("lr", "LR"), ("xgb", "XGB")]:
        with (ROOT / "models" / f"{prefix}-Pipeline.pkl").open("rb") as file:
            PIPELINES[name] = pickle.load(file)
        if list(PIPELINES[name].feature_names_in_) != FEATURES:
            raise ValueError("Pipeline sensor order does not match this TP4 schema.")
    return PIPELINES


def infer(payload, selected="lr"):
    if selected not in ["lr", "xgb"]:
        raise ValueError("Choose lr or xgb.")
    if not isinstance(payload, dict) or not isinstance(payload.get("device_id"), str):
        raise ValueError("A JSON object with device_id is required.")
    device_id = payload["device_id"]
    if not device_id or len(device_id) > 64:
        raise ValueError("device_id must contain 1–64 characters.")
    readings = payload.get("readings")
    if not isinstance(readings, dict) or any(name not in readings for name in FEATURES):
        raise ValueError("readings must contain all 12 named TP2 sensor values.")
    values = [readings[name] for name in FEATURES]
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in values):
        raise ValueError("Sensor values must be finite numbers.")
    frame = pd.DataFrame([values], columns=FEATURES)
    start = time.perf_counter()
    decisions = {}
    for name, pipeline in load_models().items():
        decisions[name] = {"prediction": int(pipeline.predict(frame)[0]),
                           "probability": float(pipeline.predict_proba(frame)[0, 1])}
    return {
        "device_id": device_id, "request_id": payload.get("request_id", 0),
        "model": selected, **decisions[selected], "both_models": decisions,
        "timestamp": time.time(), "server_inference_ms": (time.perf_counter() - start) * 1000,
    }
