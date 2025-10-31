import logging

from fastapi import FastAPI, Query, HTTPException, status
from typing import Literal
from app.services import resume_generator
from app.models import ResumeRequest, ResumeResponse
from app.utils.expoter import generate_resume_docx
from app.core.logging_utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/generate_resume", summary="Получение резюме")
def create_resume(
    data: ResumeRequest,
    lang: Literal["en", "ru", "kz"] = Query("en"),
    gen_file: bool = False,
):
    """Generate resume content via OpenAI and optionally produce a DOCX file."""
    logger.info("Generating resume for %s (lang=%s, gen_file=%s)", data.full_name, lang, gen_file)
    result = resume_generator.request(input_data=data, lang=lang)
    if not result.get("ok"):
        logger.error("Resume generation failed for %s: %s", data.full_name, result.get("error"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error"),
        )
    resume = result.get("result")
    if gen_file:
        logger.debug("Generating DOCX file for %s", data.full_name)
        generate_resume_docx(resume.dict(), title_file=data.full_name)
    logger.info("Resume generation completed for %s", data.full_name)
    return resume


@app.post("/export_resume", summary="Генерация файла резюме")
def generate_resume_file(data: ResumeResponse):
    """Create a DOCX resume file from prepared resume data."""
    logger.info("Exporting resume to DOCX")
    path = generate_resume_docx(data.dict())
    logger.info("Resume exported to %s", path)
    return path
