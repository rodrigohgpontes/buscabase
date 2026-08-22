from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.routers import router

app = FastAPI(
    title="Busca Base API",
    version="0.1.0",
    description="Por código, Buscar e Perguntar sobre o recorte validado da BNCC.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.origin, settings.public_origin, "http://localhost", "http://127.0.0.1"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.middleware("http")
async def restore_stripped_api_prefix(request: Request, call_next):
    # O Traefik do Coolify (PathPrefix /api) remove o prefixo. As rotas do FastAPI ficam em /api.
    path = request.scope.get("path") or ""
    if not path.startswith("/api"):
        request.scope["path"] = "/api" + (path if path.startswith("/") else f"/{path}")
        request.scope["raw_path"] = request.scope["path"].encode()
    return await call_next(request)


def _erro(titulo: str, texto: str) -> dict:
    return {"titulo": titulo, "texto": texto}


@app.exception_handler(StarletteHTTPException)
async def http_exception(_: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, str) and detail in {"Not Found", "Não encontrado"}:
        detail = _erro(
            "Não encontramos este endereço.",
            "Confira o endereço ou volte à busca.",
        )
    elif isinstance(detail, str) and detail in {"Method Not Allowed", "Método não permitido"}:
        detail = _erro(
            "Este método não é permitido neste endereço.",
            "Tente novamente pela interface do Busca Base.",
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=dict(exc.headers or {}),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception(_: Request, __: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": _erro(
                "Os dados enviados não estão no formato esperado.",
                "Confira os campos e tente novamente.",
            )
        },
    )


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": _erro(
                "Não foi possível concluir a busca agora.",
                "Sua consulta foi preservada. Tente novamente.",
            )
        },
    )


def _upgrade_db() -> None:
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


@app.on_event("startup")
def startup() -> None:
    try:
        _upgrade_db()
    except Exception:
        pass
