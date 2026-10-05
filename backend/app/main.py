from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import licenses, products, users
from app.services import Conflict, NotFound

app = FastAPI(
    title="License Management Portal API",
    version="1.0.0",
    description="Issue, validate, and revoke software license keys.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFound)
def _not_found(_: Request, exc: NotFound):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(Conflict)
def _conflict(_: Request, exc: Conflict):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}


for r in (users.router, products.router, licenses.router):
    app.include_router(r, prefix="/api")
