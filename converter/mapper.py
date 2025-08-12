"""Mapper: turns callables into tentative REST operations using heuristics and optional LLM help.

Output: list of operations with: method, path_template, params -> location, summary
"""
import re
from typing import Dict, Any, List
from .openai_client import ask_llm


VERB_TO_HTTP = {
    "get": "GET",
    "list": "GET",
    "read": "GET",
    "create": "POST",
    "post": "POST",
    "delete": "DELETE",
    "remove": "DELETE",
    "update": "PATCH",
    "patch": "PATCH",
    "put": "PUT",
}


def infer_verb_from_name(name: str) -> str:
    for k, v in VERB_TO_HTTP.items():
        if name.lower().startswith(k):
            return v
    return "POST"


def simple_plural(noun: str) -> str:
    if noun.endswith("y"):
        return noun[:-1] + "ies"
    return noun + "s"


def map_callable(item: Dict[str, Any], use_llm: bool = False) -> Dict[str, Any]:
    qual = item["qualname"]
    doc = item.get("doc", "")
    sig = item.get("signature")
    # derive resource from qualname e.g., CoreV1Api.read_namespaced_pod -> pod
    resource = re.split(r"[._]", qual)[-1]
    # strip leading verb-like parts
    resource = re.sub(r'^(get_|read_|create_|list_|delete_|update_)','', resource, flags=re.I)
    http = infer_verb_from_name(qual)
    path = f"/{simple_plural(resource)}"

    params = []
    for pname, p in sig.parameters.items():
        if pname in ("self", "kwargs"):
            continue
        # heuristics: id-like -> path param
        if re.search(r"(name|id|namespace|owner|repo|resource)", pname, re.I):
            params.append({"name": pname, "in": "path", "required": True})
            path += f"/{{{pname}}}"
        else:
            params.append({"name": pname, "in": "query", "required": p.default == p.empty})

    op = {
        "operationId": qual.replace('.', '_'),
        "http_method": http,
        "path": path,
        "summary": doc.split('\n')[0] if doc else qual,
        "params": params,
    }

    if use_llm:
        prompt = f"Map this SDK method to a REST endpoint.\nMethod: {qual}\nSignature: {sig}\nDoc: {doc}\nCurrent mapping: {op}\nReturn JSON with keys: http_method, path, params where params include name and in(path|query|body). Keep it short."
        llm = ask_llm(prompt)
        if llm:
            # naive: try to parse simple lines like "http_method: GET\npath: /pods/{name}\nparams: name:path"
            for line in llm.splitlines():
                if line.lower().startswith("http_method"):
                    op["http_method"] = line.split(":",1)[1].strip()
                if line.lower().startswith("path"):
                    op["path"] = line.split(":",1)[1].strip()
                if line.lower().startswith("params"):
                    pass
    return op


def map_many(items: List[Dict[str, Any]], use_llm: bool = False) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        try:
            out.append(map_callable(it, use_llm=use_llm))
        except Exception as e:
            print("Mapping failed for", it.get('qualname'), e)
    return out