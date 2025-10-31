from openai import OpenAI, APIConnectionError, AuthenticationError
import httpx
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key.get_secret_value())


def test():
    try:
        response = client.responses.create(
            model="gpt-5", input="Write a one-sentence bedtime story about a unicorn."
        )
        return {"ok": True, "result": response.output_text}
    except AuthenticationError:
        return {"ok": False, "error": "Wrong openai key"}
    except APIConnectionError:
        return {"ok": False, "error": "Can't connect to openai"}
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError):
        return {"ok": False, "error": "Network error"}
