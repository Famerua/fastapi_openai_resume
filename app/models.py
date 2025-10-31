from pydantic import BaseModel

class ResumeResponse(BaseModel):
    resume_text: str
    summary: str
