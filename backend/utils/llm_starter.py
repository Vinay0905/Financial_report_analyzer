from openai import OpenAI
from ..config.settings import Settings

OPENAI_API_KEY = Settings.OPENAI_API_KEY


def summarize(text):
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": "Summarize:"}, {"role": "user", "content": text}]
    )
    return resp.choices[0].message.content if resp and resp.choices else ""
