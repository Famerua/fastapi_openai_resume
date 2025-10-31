from fastapi import FastAPI, Query
from typing import Literal
from app.services import resume_generator
from app.models import ResumeRequest

app = FastAPI()


@app.post("/generate_resume", summary="Получение резюме")
def create_resume(data: ResumeRequest, lang: Literal["en", "ru", "kz"] = Query("en")):
    result = resume_generator.request(input_data=data, lang=lang)
    if not result.get("ok"):
        return f"ERROR, {result.get('error')}"
    return result.get("result")
