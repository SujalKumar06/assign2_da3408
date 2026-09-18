import os
import socket

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis

MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")
POD_NAME = os.environ.get("POD_NAME", socket.gethostname())
NODE_NAME = os.environ.get("NODE_NAME", "unknown")
REDIS_HOST = os.environ.get("REDIS_HOST", "cache")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_TTL = int(os.environ.get("REDIS_TTL", "367"))

app = FastAPI(title="Spam Detection API")
_bundle = None

@app.on_event("startup")
def load_model():
    global _bundle
    global r
    _bundle = joblib.load(MODEL_PATH)
    r = redis.Redis(host = REDIS_HOST, port = REDIS_PORT, decode_responses=True)
    print(
        f"Loaded model {_bundle['model_version']} (labels={_bundle['labels']}) "
        f"on pod={POD_NAME} node={NODE_NAME}",
        flush=True,
    )


class PredictRequest(BaseModel):
    text: str

@app.get("/healthz")
def healthz():
    if _bundle is None:
        return JSONResponse(
            status_code=503,
            content={"status": "loading", "pod": POD_NAME, "node": NODE_NAME},
        )
    return {
        "status": "ok",
        "version": "v2",
        "pod": POD_NAME,
        "node": NODE_NAME,
    }

@app.post("/predict")
def predict(request: PredictRequest):
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if r.exists(request.text):
        label = r.get(request.text)
    else:
        label = _bundle["model"].predict([request.text])[0]
        r.setex(request.text, REDIS_TTL, label)

    return {
        "label": label
    }
