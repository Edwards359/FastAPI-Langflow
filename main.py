import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

client: Optional[httpx.AsyncClient] = None

LANGFLOW_URL = (os.getenv("LANGFLOW_URL") or "").rstrip("/")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID") or ""
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY") or ""
LANGFLOW_INPUT_TYPE = os.getenv("LANGFLOW_INPUT_TYPE") or "chat"
LANGFLOW_OUTPUT_TYPE = os.getenv("LANGFLOW_OUTPUT_TYPE") or "chat"

LOVEABLE_ORIGIN = os.getenv("LOVEABLE_ORIGIN") or ""
CORS_ALLOW_ALL = (os.getenv("CORS_ALLOW_ALL") or "").lower() in ("1", "true", "yes")

missing: List[str] = []
if not LANGFLOW_URL:
    missing.append("LANGFLOW_URL")
if not LANGFLOW_FLOW_ID:
    missing.append("LANGFLOW_FLOW_ID")

if missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

timeout = httpx.Timeout(connect=10.0, read=120.0, write=120.0, pool=10.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = httpx.AsyncClient(timeout=timeout, trust_env=False)
    yield
    await client.aclose()

app = FastAPI(title="Langflow FastAPI Proxy", lifespan=lifespan)

allow_origins = ["*"] if CORS_ALLOW_ALL else ([LOVEABLE_ORIGIN] if LOVEABLE_ORIGIN else [])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class MultiplyRequest(BaseModel):
    numbers: List[float] = Field(min_length=2)
    session_id: Optional[str] = None

def _extract_text_from_langflow(resp_json: Dict[str, Any]) -> str:
    try:
        return resp_json["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to extract text: {e!r}") from e

def _make_auth_headers() -> List[Dict[str, str]]:
    headers = [{"Content-Type": "application/json"}]
    if LANGFLOW_API_KEY:
        return [
            {**headers[0], "Authorization": f"Bearer {LANGFLOW_API_KEY}"},
            {**headers[0], "x-api-key": LANGFLOW_API_KEY},
        ]
    return headers

async def _run_langflow(input_value: str, session_id: str) -> Tuple[Dict[str, Any], str]:
    url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    payload = {
        "input_value": input_value,
        "input_type": LANGFLOW_INPUT_TYPE,
        "output_type": LANGFLOW_OUTPUT_TYPE,
        "session_id": session_id,
        "tweaks": {},
    }

    last_status = None
    last_text = None

    for headers in _make_auth_headers():
        try:
            r = await client.post(url, json=payload, headers=headers)
            last_status = r.status_code
            last_text = r.text
            if r.status_code in (401, 403) and LANGFLOW_API_KEY:
                continue
            r.raise_for_status()
            auth_used = "none"
            if "Authorization" in headers:
                auth_used = "bearer"
            elif "x-api-key" in headers:
                auth_used = "x-api-key"
            return r.json(), auth_used
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Langflow request error: {type(e).__name__}: {e}") from e

    raise HTTPException(
        status_code=502,
        detail=f"Langflow auth failed. Last status={last_status}. Last response={last_text}",
    )

@app.get("/")
async def root():
    return {"status": "up"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/multiply")
async def multiply(req: MultiplyRequest):
    input_value = " * ".join(str(x) for x in req.numbers)
    resp_json, auth_used = await _run_langflow(
        input_value=input_value,
        session_id=req.session_id or "multiply-session",
    )
    return {
        "input": input_value,
        "auth_used": auth_used,
        "result_text": _extract_text_from_langflow(resp_json),
        "raw": resp_json,
    }
