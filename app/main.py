from fastapi import FastAPI
from app.services import resume_generator


app = FastAPI()


@app.get("/")
def hello():
    return resume_generator.test()
