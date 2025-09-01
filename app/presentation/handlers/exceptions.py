# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/presentation/handlers/exceptions.py

"""
Centralized exception handlers for the application.
"""


from app.domain.exceptions import (
    ResourceAlreadyExistsError,
    DatabaseError,
    ValidationError,
    CollectionNotFoundError,
    ResourceNotFoundError
)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging

# Set up a logger for the application
logger = logging.getLogger("fastapi_app")


def register_exception_handlers(app: FastAPI):

    # This handler will catch the error from the service layer
    @app.exception_handler(ResourceAlreadyExistsError)
    async def resource_already_exists_handler(request: Request, exc: ResourceAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    # This handler will catch the validation error
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    # This handler will catch the generic database error
    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "A problem occurred with a downstream service."},
        )

    @app.exception_handler(CollectionNotFoundError)
    async def collection_not_found_handler(req: Request, exc: CollectionNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(req: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
