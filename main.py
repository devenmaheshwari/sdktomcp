import importlib
import inspect
import argparse
import os
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import pkgutil
import inspect

# Get API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your environment before running.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()


def load_sdk_functions(sdk_name):
    sdk_module = importlib.import_module(sdk_name)
    functions = {}

    def walk_module(mod):
        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj):
                full_name = f"{mod.__name__}.{name}"
                functions[full_name] = obj
            elif inspect.isclass(obj):
                for meth_name, meth in inspect.getmembers(obj, inspect.isfunction):
                    full_name = f"{mod.__name__}.{obj.__name__}.{meth_name}"
                    functions[full_name] = meth
        if hasattr(mod, "__path__"):  # package
            for _, subname, ispkg in pkgutil.iter_modules(mod.__path__):
                submodule = importlib.import_module(f"{mod.__name__}.{subname}")
                walk_module(submodule)

    walk_module(sdk_module)
    return functions


def create_endpoint(func_name, func):
    @app.post(f"/{func_name}")
    def endpoint(**kwargs):
        try:
            result = func(**kwargs)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

def generate_endpoints(sdk_name):
    functions = load_sdk_functions(sdk_name)
    for func_name, func in functions.items():
        if inspect.isfunction(func):
            create_endpoint(func_name, func)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", required=True, help="SDK name to convert (e.g., kubernetes, github, azure.mgmt.resource)")
    args = parser.parse_args()

    generate_endpoints(args.sdk)
    uvicorn.run(app, host="0.0.0.0", port=8000)

