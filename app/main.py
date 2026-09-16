"""
main.py — AIOps Module 3 Assignment
FastAPI spam-detection service. Loads the model exported by train.py.

  POST /predict   {"text": "..."} -> {"label": "spam"|"ham"}
  GET  /healthz   HTTP 200 once the model is loaded, 503 before
"""
import os
import socket
import time
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")
POD_NAME = os.environ.get("POD_NAME", socket.gethostname())
NODE_NAME = os.environ.get("NODE_NAME", "unknown")

_bundle = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bundle
    _bundle = joblib.load(MODEL_PATH)
    print(
        f"Loaded model {_bundle['model_version']} (labels={_bundle['labels']}) "
        f"on pod={POD_NAME} node={NODE_NAME}",
        flush=True,
    )
    yield
    _bundle = None


app = FastAPI(title="Spam Detection API", lifespan=lifespan)


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1)


@app.get("/healthz")
def healthz():
    if _bundle is None:
        return JSONResponse(
            status_code=503,
            content={"status": "loading", "pod": POD_NAME, "node": NODE_NAME},
        )
    return {
        "status": "ok",
        "model_version": _bundle["model_version"],
        "pod": POD_NAME,
        "node": NODE_NAME,
    }


@app.post("/predict")
def predict(request: PredictRequest):
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    t0 = time.perf_counter()
    label = _bundle["model"].predict([request.text])[0]
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)

    return {
        "label": label,
        "latency_ms": latency_ms,
        "served_by_pod": POD_NAME,
        "served_by_node": NODE_NAME,
    }
