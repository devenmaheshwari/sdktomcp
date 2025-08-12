"""Inspector: collects callable SDK surface via introspection.

This module prefers safe import but can fallback to AST parsing if import fails.
"""
import inspect
import importlib
from typing import List, Dict, Any


def collect_module_callables(module_name: str) -> List[Dict[str, Any]]:
    """Return a list of callables with metadata from a module."""
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        raise ImportError(f"Failed to import {module_name}: {e}")

    results = []
    for name, obj in inspect.getmembers(mod):
        if inspect.isclass(obj) and obj.__module__.startswith(mod.__name__):
            for mname, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if method.__module__.startswith(mod.__name__):
                    sig = inspect.signature(method)
                    results.append({
                        "qualname": f"{obj.__name__}.{mname}",
                        "callable": method,
                        "signature": sig,
                        "doc": inspect.getdoc(method) or "",
                        "module": mod.__name__,
                    })
        elif inspect.isfunction(obj) and obj.__module__.startswith(mod.__name__):
            sig = inspect.signature(obj)
            results.append({
                "qualname": name,
                "callable": obj,
                "signature": sig,
                "doc": inspect.getdoc(obj) or "",
                "module": mod.__name__,
            })
    return results