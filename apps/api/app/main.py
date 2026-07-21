"""ADD FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.simulation import router as simulation_router


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://engineering-air-deflector-designer.vercel.app",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(simulation_router, prefix="/api/v1")


@app.get("/api/v1/health/live")
def live() -> dict[str, str]:
    """Report process liveness."""

    return {"status": "ok"}
