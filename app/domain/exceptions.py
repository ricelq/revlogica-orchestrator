# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/domain/exceptions.py

"""
This module defines the custom, application-specific exceptions for the domain layer.

These exceptions represent specific business rule violations or domain-level errors.
They are technology-agnostic and contain no details about the presentation layer
(e.g., HTTP status codes), ensuring a clean separation of concerns.
"""

# ==============================
# Base Application Exception
# ==============================


class ApplicationException(Exception):
    """Base class for all custom exceptions in this application."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

# =======================================
# Data Access & Repository Exceptions
# =======================================


class RepositoryError(ApplicationException):
    """Base exception for errors originating from the data access layer."""
    pass


class ResourceNotFoundError(RepositoryError):
    """Raised when a specific resource (e.g., a document) is not found."""
    pass


class CollectionNotFoundError(ResourceNotFoundError):
    """
    Raised specifically when a collection is not found. 
    Inherits from ResourceNotFoundError for potential generic handling.
    """
    pass


class ResourceAlreadyExistsError(RepositoryError):
    """Raised when attempting to create a resource that already exists."""
    pass


class DatabaseError(RepositoryError):
    """Raised for generic database communication or operational errors."""
    pass

# ==========================================
# Business Logic & Validation Exceptions
# ==========================================


class ValidationError(ApplicationException):
    """Raised when business rule validation or data integrity fails."""
    pass
