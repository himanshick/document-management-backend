from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED
from app.core.logger import get_logger
logger = get_logger()

def add_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation failed: {exc.errors()}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation failed", "errors": exc.errors()},
        )

    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        logger.warning("Invalid or expired token")
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
