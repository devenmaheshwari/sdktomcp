"""FastAPI app that wires generated operations to a simple dispatcher.

This prototype supports calling local Python callables by importing a module and finding the callable by name.
"""
from fastapi import FastAPI, Path, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import importlib
import json

app = FastAPI(title="SDK-to-MCP Prototype")

# Keep a mapping registry in-memory for demo. In the real generator this is created from OpenAPI.
ROUTES = []


@app.on_event("startup")
async def startup_event():
    # try to load a generated routes.json if present
    try:
        with open('routes.json') as f:
            routes = json.load(f)
            for r in routes:
                ROUTES.append(r)
    except FileNotFoundError:
        pass


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/register")
async def register_route(route: dict):
    """Register a single mapped operation at runtime for demo purposes."""
    ROUTES.append(route)
    return {"registered": route}


@app.api_route("/invoke", methods=["POST"])  # generic invoker for demo
async def invoke(payload: dict = Body(...)):
    """Invoke a registered SDK callable by operationId.

    payload: {"operationId":"...","args":{...}}
    """
    opid = payload.get("operationId")
    if not opid:
        raise HTTPException(status_code=400, detail="operationId required")
    route = next((r for r in ROUTES if r.get("operationId") == opid), None)
    if not route:
        raise HTTPException(status_code=404, detail="operation not found")

    # for prototype, the operationId encodes module:qualname, e.g., github.Github.get_user
    # We'll expect route to include a field 'callable' with "module:qualname"
    target = route.get("callable")
    if not target:
        raise HTTPException(status_code=500, detail="no callable configured")
    modname, qual = target.split(":", 1)
    try:
        mod = importlib.import_module(modname)
    except Exception as e:
        raise HTTPException(status_code=500)