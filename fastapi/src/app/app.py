from functools import lru_cache

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from src.app.configs.config import settings
from src.app.configs.database import init_db
from src.app.routers import auth
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi import FastAPI

app = FastAPI()
app.include_router(auth.router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@lru_cache()
def get_settings():
    return settings


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/", tags=["root"])
async def root():
    return RedirectResponse("/docs")
