# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/application/services/existdb_service.py

from app.domain.exceptions import (
    CollectionNotFoundError,
    DatabaseError,
    ResourceAlreadyExistsError,
    DatabaseError,
    ValidationError,
    ResourceNotFoundError
)


from typing import Optional, List
import logging

from app.application.interfaces.existdb_repository_interface import ExistDBRepositoryInterface
import httpx
from lxml import etree as ET


# Set up logging for the service
logger = logging.getLogger(__name__)


class ExistDBService:
    """
    A service class that contains the business logic for managing documents in ExistDB.

    This layer orchestrates repository calls and contains all business rules.
    """

    def __init__(self, repository: ExistDBRepositoryInterface):
        """
        Initializes the service with a repository instance.
        The repository is injected as a dependency.
        """
        self.repository = repository

    async def create_document(self, collection: str, document_name: str, content: str) -> None:
        """
        Creates a new document. Returns None on success.

        Raises:
            ValidationError: If input parameters are missing.
            ResourceAlreadyExistsError: If the document already exists and cannot be overwritten.
            DatabaseError: For other database-related communication errors.
        """
        if not all([collection, document_name, content]):
            logger.warning("Attempted to create document with missing input.")
            # Raise a specific validation error.
            raise ValidationError(
                "Collection, document_name, and content are required.")

        # --- "Look Before You Leap" ---
        # Check if the document exists.
        if await self.document_exists(collection, document_name):
            raise ResourceAlreadyExistsError(
                f"Cannot create because document '{document_name}' already exists."
            )

        # If the check passes, proceed with creation.
        try:
            await self.repository.put(collection, document_name, content)

        except httpx.HTTPStatusError as e:
            # --- TRANSLATION STEP ---
            # Translate the low-level HTTP error into a high-level, generic DatabaseError.
            # The specific details are logged, but the endpoint only needs to know that the database failed.
            logger.error(f"A downstream database error occurred: {e}")
            raise DatabaseError(
                "Failed to create document due to a database error.") from e

    async def get_document(self, collection: str, document_name: str) -> str:
        """
        Retrieves a document.

        Raises:
            ResourceNotFoundError: If the requested document does not exist.
            DatabaseError: For any other database communication errors.
        """
        try:
            # The repository will now either return the content string or raise an error.
            return await self.repository.get(collection, document_name)
        except httpx.HTTPStatusError as e:
            # --- TRANSLATION STEP ---
            if e.response.status_code == 404:
                # Translate the technical 404 into a specific, meaningful business exception.
                raise ResourceNotFoundError(
                    f"The document '{document_name}' in collection '{collection}' was not found."
                ) from e
            else:
                # Translate all other HTTP errors into a generic database error.
                raise DatabaseError(
                    "A database error occurred while fetching the document.") from e

    async def update_document(self, collection: str, document_name: str, new_content: str) -> None:
        """
        Updates an existing document with new content. Returns None on success.

        Raises:
            ResourceNotFoundError: If the document to be updated does not exist.
            DatabaseError: For any other database communication errors.
        """
        try:
            # Ensure the document exists before trying to update it.
            # We call the repository's get method. If it fails with a 404, the
            # specific ResourceNotFoundError will be raised below.
            await self.repository.get(collection, document_name)

            # If the document exists, proceed with the update.
            # The 'put' method will overwrite the content.
            await self.repository.put(collection, document_name, new_content)

        except httpx.HTTPStatusError as e:
            # --- TRANSLATION STEP ---
            if e.response.status_code == 404:
                # If the initial 'get' check failed, translate it to a business exception.
                raise ResourceNotFoundError(
                    f"Cannot update because document '{document_name}' was not found."
                ) from e
            else:
                # Translate any other HTTP error (from get or put) into a generic DatabaseError.
                raise DatabaseError(
                    "A database error occurred while updating the document.") from e

    async def delete_document(self, collection: str, document_name: str) -> None:
        """
        Deletes a document. Returns None on success.

        Raises:
            ResourceNotFoundError: If the document to be deleted does not exist.
            DatabaseError: For any other database communication errors.
        """
        try:
            # The repository will now either succeed or raise an exception.
            await self.repository.delete(collection, document_name)
        except httpx.HTTPStatusError as e:
            # --- TRANSLATION STEP ---
            if e.response.status_code == 404:
                # Translate the technical 404 into a specific, meaningful business exception.
                raise ResourceNotFoundError(
                    f"Cannot delete because document '{document_name}' was not found."
                ) from e
            else:
                # Translate all other HTTP errors into a generic database error.
                raise DatabaseError(
                    "A database error occurred while deleting the document.") from e

    async def list_documents_in_collection(self, collection: str) -> List[str]:
        """
        Lists all document names within a collection.

        Raises:
            CollectionNotFoundError: If the specified collection does not exist.
            DatabaseError: For other database or parsing-related errors.
        """
        try:
            # The repository will either return a list or raise an exception.
            return await self.repository.list_documents(collection=collection)
        except httpx.HTTPStatusError as e:
            # --- TRANSLATION STEP ---
            if e.response.status_code == 404:
                # Translate the technical 404 into a specific business exception.
                raise CollectionNotFoundError(
                    f"The collection '{collection}' was not found.") from e
            else:
                # Translate all other HTTP errors into a generic database error.
                raise DatabaseError(
                    "A database error occurred while listing documents.") from e
        except ET.XMLSyntaxError as e:
            # Also translate parsing errors.
            raise DatabaseError(
                "Failed to parse the database response.") from e

    async def document_exists(self, collection: str, document_name: str) -> bool:
        """
        Checks if a document exists.

        Raises:
            DatabaseError: For any unexpected database communication errors.
        """
        try:
            return await self.repository.exists(collection, document_name)
        except httpx.HTTPStatusError as e:
            # Translate any unexpected error from the repository into a high-level one.
            raise DatabaseError(
                "A database error occurred while checking for the document.") from e
