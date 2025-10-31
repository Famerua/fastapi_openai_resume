from fastapi import FastAPI
from app.services import resume_generator
from app.models import ResumeRequest

app = FastAPI()


@app.post("/generate_resume", summary="Получение резюме")
def create_resume(data: ResumeRequest):
    result = resume_generator.request(input_data=data)
    if not result.get("ok"):
        return f"ERROR, {result.get('error')}"
    return result.get("result")