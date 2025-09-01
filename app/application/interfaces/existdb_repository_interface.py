# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================


# revlogica-orchestrator/app/application/interfaces/existdb_repository_interface.py


from abc import ABC, abstractmethod
from typing import List, Optional


class ExistDBRepositoryInterface(ABC):
    """
    An abstract base class (interface) for an ExistDB repository.

    This interface defines the contract that any concrete ExistDB repository
    implementation must follow.
    """

    @abstractmethod
    def get(self, collection: str, document_name: str) -> Optional[str]:
        """Retrieves a single document from ExistDB."""
        pass

    @abstractmethod
    def put(self, collection: str, document_name: str, content: str, overwrite: bool = False) -> bool:
        """Saves or updates a document in ExistDB."""
        pass

    @abstractmethod
    def delete(self, collection: str, document_name: str) -> bool:
        """Deletes a document from ExistDB."""
        pass

    @abstractmethod
    def create_collection(self, collection_name: str) -> bool:
        """Creates a new collection in ExistDB."""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """Deletes a collection and all its contents from ExistDB."""
        pass

    @abstractmethod
    def query(self, xpath_expression: str) -> List[str]:
        """Executes an XPath query and returns matching documents."""
        pass

    @abstractmethod
    def list_documents(self, collection: str) -> List[str]:
        """Lists all document names in a specified collection."""
        pass
