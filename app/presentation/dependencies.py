# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/presentation/dependencies.py

from functools import lru_cache

from app.infrastructure.repositories.existdb_repository import ExistDBRepository
from app.application.services.existdb_service import ExistDBService
from app.application.interfaces.existdb_repository_interface import ExistDBRepositoryInterface


@lru_cache()
def get_existdb_repository() -> ExistDBRepositoryInterface:
    """Provides a singleton instance of the ExistDB repository."""
    return ExistDBRepository()


@lru_cache()
def get_existdb_service() -> ExistDBService:
    """
    Provides a singleton instance of the ExistDB service.

    The service is injected with the repository dependency.
    """
    repository = get_existdb_repository()
    return ExistDBService(repository=repository)
