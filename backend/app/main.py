import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import verification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Objection Anonymous Source Verification API",
    description="Privacy-preserving evidence verification system",
    version="1.0.0",
)

certificate_store: dict = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verification.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc

    import traceback

    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {exc}"},
    )


@app.on_event("startup")
async def log_startup_config() -> None:
    groq_configured = bool(os.getenv("GROQ_API_KEY"))
    logger.info(
        "API startup: groq_configured=%s internal_api=%s",
        groq_configured,
        os.getenv("INTERNAL_API_URL", "not set"),
    )
    if not groq_configured:
        logger.warning(
            "GROQ_API_KEY is not set — /api/verify/ will return 503 until configured"
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "objection-verification-api",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
