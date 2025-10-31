from fastapi import FastAPI, Query, HTTPException, status
from typing import Literal
from app.services import resume_generator
from app.models import ResumeRequest, ResumeResponse
from app.utils.expoter import generate_resume_docx

app = FastAPI()


@app.post("/generate_resume", summary="Получение резюме")
def create_resume(
    data: ResumeRequest,
    lang: Literal["en", "ru", "kz"] = Query("en"),
    gen_file: bool = False,
):
    result = resume_generator.request(input_data=data, lang=lang)
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error"),
        )
    resume = result.get("result")
    if gen_file:
        generate_resume_docx(resume.dict(), title_file=data.full_name)
    return resume


@app.post("/export_resume", summary="Генерация файла резюме")
def generate_resume_file(data: ResumeResponse):
    path = generate_resume_docx(data.dict())
    return path
