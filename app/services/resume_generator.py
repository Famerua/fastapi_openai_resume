from openai import OpenAI, APIConnectionError, AuthenticationError
import httpx
from app.core.config import settings
from app.models import ResumeResponse


client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

input_data = {
    "full_name": "Taubay Kozhagaliyev",
    "position": "Python SoftWare Developer",
    "skills": ["Django", "SQL", "FastAPI"],
    "experience": "3 years like python developr since 2022",
    "education": "Bachelor of MIPT",
    "languages": ["English - B2", "Kazakh - Native", "Russian - fluent"],
}


def test():
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
