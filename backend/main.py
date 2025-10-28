from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings


app = FastAPI(
    title="Shadow Role API",
    description="API for the Shadow Role web app",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host=settings.API_HOST, port=int(settings.API_PORT), reload=True)

