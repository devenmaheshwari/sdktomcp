"""Generate a minimal OpenAPI spec from mapped operations."""
import yaml
from typing import List, Dict, Any


def generate_openapi(operations: List[Dict[str, Any]], title: str = "SDK-MCP") -> Dict[str, Any]:
    o = {
        "openapi": "3.0.0",
        "info": {"title": title, "version": "0.1.0"},
        "paths": {},
        "components": {"schemas": {}},
    }
    for op in operations:
        p = op["path"]
        path_obj = o["paths"].setdefault(p, {})
        # minimal parameter -> OpenAPI mapping
        parameters = []
        requestBody = None
        for prm in op["params"]:
            if prm["in"] == "path" or prm["in"] == "query":
                parameters.append({
                    "name": prm["name"],
                    "in": prm["in"],
                    "required": prm.get("required", False),
                    "schema": {"type": "string"},
                })
            elif prm["in"] == "body":
                requestBody = {
                    "content": {"application/json": {"schema": {"type": "object"}}}
                }
        path_obj[op["http_method"].lower()] = {
            "summary": op.get("summary"),
            "operationId": op["operationId"],
            "parameters": parameters,
            **({"requestBody": requestBody} if requestBody else {}),
            "responses": {"200": {"description": "OK"}},
        }
    return o


def dump_openapi_yaml(openapi: Dict[str, Any], path: str):
    with open(path, "w") as f:
        yaml.safe_dump(openapi, f)