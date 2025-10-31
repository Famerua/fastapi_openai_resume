from pydantic import BaseModel, constr, Field


class ResumeResponse(BaseModel):
    """Use to struct openai api output https://platform.openai.com/docs/guides/structured-outputs"""

    resume_text: str
    summary: str


LanguageLevel = constr(pattern=r"^[A-Za-z\s]+ - [A-Za-z0-9]+$")


class ResumeRequest(BaseModel):
    full_name: str = Field(..., example="Kozhagaliyev Taubay")
    position: str = Field(..., example="Python Softwate Developer")
    skills: list[str] = Field(..., example=["Python", "SQL", "FastAPI"])
    experience: str = Field(
        ..., example="3 years in backend development, banking automation projects"
    )
    education: str = Field(..., example="Bachelor in Computer Science")
    languages: list[LanguageLevel] = Field(..., example=["English - B2", "Kazakh - native", "Russian - fluent"])  # type: ignore
