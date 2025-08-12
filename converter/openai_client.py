"""Small wrapper for optional OpenAI usage.

If OPENAI_API_KEY not set, calls to `ask_llm` return None.
"""
import os


OPENAI_KEY = os.getenv("OPENAI_API_KEY")


def ask_llm(prompt: str) -> str | None:
    if not OPENAI_KEY:
        return None
    try:
        import openai
        openai.api_key = OPENAI_KEY
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.0,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print("LLM call failed:", e)
        return None