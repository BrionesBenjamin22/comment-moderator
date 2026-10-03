from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.classifier import Classifier, FakeClassifier
from app.config import Settings, get_settings
from app.db.connection import check_database, make_engine, make_session_factory
from app.schemas.moderation import HealthResponse


def create_app(settings: Settings | None = None, classifier: Classifier | None = None) -> FastAPI:
    settings = settings or get_settings()
    engine = make_engine(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        engine.dispose()

    app = FastAPI(title="Butchery Moderation Lab", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = make_session_factory(engine)
    app.state.classifier = classifier if classifier is not None else FakeClassifier()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Revisá los datos ingresados e intentá nuevamente.",
                }
            },
        )

    @app.get("/health", response_model=HealthResponse)
    def health():
        try:
            check_database(engine)
        except SQLAlchemyError:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unavailable",
                    "database": "unavailable",
                },
            )
        return HealthResponse(status="ok", database="ok")

    return app
