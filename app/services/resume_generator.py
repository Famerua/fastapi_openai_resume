import logging

from openai import OpenAI, APIConnectionError, AuthenticationError
import httpx
from app.core.config import settings
from app.models import ResumeResponse, ResumeRequest
from app.consts import RESPONSE_BLOCKS, LANGUAGES

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key.get_secret_value())


def get_system_msg(lang: str) -> str:
    """Build the system prompt tailored to the requested language."""
    blocks = RESPONSE_BLOCKS[lang]
    return (
        "You are a professional resume writer.\n"
        "Output must be valid JSON that matches the SDK model (two fields only: resume_text, summary).\n"
        "Language: {lang}. Use the exact section headings below in the same language.\n"
        "Inside resume_text, produce Markdown with EXACTLY these H2 sections and in this order:\n"
        f"## {blocks[0]}\n"
        f"## {blocks[1]}\n"
        f"## {blocks[2]}\n"
        f"## {blocks[3]}\n"
        f"## {blocks[4]}\n\n"
        "Formatting rules:\n"
        f"- In '{blocks[1]}' list skills as bullet points.\n"
        f"- In '{blocks[2]}' list roles/projects as bullets with brief impact lines.\n"
        f"- In '{blocks[3]}' list degree(s) or courses as bullets.\n"
        f"- In '{blocks[4]}' include email/phone/city (if provided) as bullets.\n"
        "Do not add extra sections or keys. Keep summary as a single short paragraph."
    ).format(lang=LANGUAGES[lang])


def request(input_data: ResumeRequest, lang: str):
    """Request resume data from OpenAI Responses API."""
    logger.debug("Calling OpenAI for %s (lang=%s)", input_data.full_name, lang)
    system_msg = get_system_msg(lang)
    try:
        response = client.responses.parse(
            model="gpt-5",
            text_format=ResumeResponse,
            input=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": (
                        f"Build resume from JSON (respond in {LANGUAGES[lang]}):\n{input_data}\n"
                        "Return JSON with keys 'resume_text' and 'summary' only."
                    ),
                },
            ],
        )
        logger.info("OpenAI resume response received for %s", input_data.full_name)
        return {"ok": True, "result": response.output_parsed}
    except AuthenticationError:
        logger.exception("Authentication error while requesting OpenAI response")
        return {"ok": False, "error": "Wrong openai key"}
    except APIConnectionError:
        logger.exception("API connection error while requesting OpenAI response")
        return {"ok": False, "error": "Can't connect to openai"}
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError):
        logger.exception("Network error while requesting OpenAI response")
        return {"ok": False, "error": "Network error"}
