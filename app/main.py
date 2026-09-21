import logging

from fastapi import FastAPI, Query, HTTPException, status
from typing import Literal
from app.api.routes import router as history_router
from app.db import repository
from app.services import resume_generator
from app.models import ResumeRequest, ResumeResponse
from app.utils.expoter import generate_resume_docx
from app.core.logging_utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(history_router)


@app.on_event("startup")
def on_startup():
    repository.init_db()


@app.post("/generate_resume", summary="Получение резюме")
async def create_resume(
    data: ResumeRequest,
    lang: Literal["en", "ru", "kz"] = Query("en"),
    gen_file: bool = False,
    user_email: str = Query("demo@example.com"),
):
    """Generate resume content via OpenAI and optionally produce a DOCX file."""
    logger.info("Generating resume for %s (lang=%s, gen_file=%s)", data.full_name, lang, gen_file)
    result = await resume_generator.request(input_data=data, lang=lang)
    if not result.get("ok"):
        logger.error("Resume generation failed for %s: %s", data.full_name, result.get("error"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error"),
        )
    resume = result.get("result")
    generation_id = repository.save_generation(
        user_email=user_email, data=data, resume=resume, lang=lang
    )
    if gen_file:
        logger.debug("Generating DOCX file for %s", data.full_name)
        path = generate_resume_docx(resume.dict(), title_file=data.full_name)
        repository.attach_file(generation_id, str(path))
    logger.info("Resume generation completed for %s", data.full_name)
    return resume


@app.post("/export_resume", summary="Генерация файла резюме")
async def generate_resume_file(data: ResumeResponse):
    """Create a DOCX resume file from prepared resume data."""
    logger.info("Exporting resume to DOCX")
    path = generate_resume_docx(data.dict())
    logger.info("Resume exported to %s", path)
    return path
