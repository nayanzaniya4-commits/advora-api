from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="AdVora AI API",
    version="1.0.0",
    description="Zero-prompt product advertising backend."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

# Serves generated templates/stickers back over HTTP as /files/<name>
app.mount("/files", StaticFiles(directory=settings.DATA_DIR), name="files")


@app.get("/health")
def health():
    return {"status": "ok", "service": "advora-api", "environment": settings.APP_ENV}
