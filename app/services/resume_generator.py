from openai import OpenAI, APIConnectionError, AuthenticationError
import httpx
from app.core.config import settings
from app.models import ResumeResponse

client = OpenAI(api_key=settings.openai_api_key.get_secret_value())


def request(input_data):
    try:
        response = client.responses.parse(
            model="gpt-5",
            text_format=ResumeResponse,
            input=[
                {"role": "system", "content": "You are a professional resume writer. Return JSON per model."},
                {"role": "user", "content": f"Build resume form {input_data}"},
            ],
        )
        return {"ok": True, "result": response.output_parsed}
    except AuthenticationError:
        return {"ok": False, "error": "Wrong openai key"}
    except APIConnectionError:
        return {"ok": False, "error": "Can't connect to openai"}
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError):
        return {"ok": False, "error": "Network error"}
