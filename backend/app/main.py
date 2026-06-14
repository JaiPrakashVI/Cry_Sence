from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import static_ffmpeg

# Add static ffmpeg binaries to PATH
static_ffmpeg.add_paths()

from backend.app.routes.audio import router as audio_router
from backend.app.routes.health import router as health_router
from backend.app.utils.config import get_settings
from backend.app.utils.logging import configure_logging
from backend.app.utils.rate_limit import InMemoryRateLimiter

settings = get_settings()
configure_logging()
LOGGER = logging.getLogger(__name__)
rate_limiter = InMemoryRateLimiter()

app = FastAPI(
    title="CrySense API",
    version="1.0.0",
    description="AI-powered emotional distress detection from uploaded or recorded audio."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health_router)
app.include_router(audio_router)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        rate_limiter.check(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    LOGGER.info("[Request Started] method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    LOGGER.info(
        "[Request Complete] method=%s path=%s status=%s elapsed_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms
    )
    return response
