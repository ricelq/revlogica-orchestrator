# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/infrastructure/repositories/existdb_repository.py


from typing import List, Optional
import logging
from urllib.parse import urlparse
import httpx
from httpx import BasicAuth
from lxml import etree as ET
import textwrap

from app.application.interfaces.existdb_repository_interface import ExistDBRepositoryInterface
from app.infrastructure.config import settings

# --- Constants for eXist-DB API Contract ---
# Centralize the namespace definition to avoid magic strings in the code.
EXISTDB_NAMESPACE = "http://exist.sourceforge.net/NS/exist"
NS_MAP = {'exist': EXISTDB_NAMESPACE}

# This query finds all 'resource' elements in the 'exist' namespace
# and directly selects their 'name' attribute.
LIST_DOCS_XPATH = '//exist:resource/@name'


# Set up logging
logger = logging.getLogger(__name__)


class ExistDBRepository(ExistDBRepositoryInterface):
    """
    # Repository to interact with the eXist-DB XML database via its REST API.

    """

    def __init__(self):
        """
        # The repository uses the base URL and credentials from the central settings.
        We use HTTPBasicAuth for explicit authentication.
        """
        self.base_url = f"{settings.existdb_url}"
        self.auth = BasicAuth(settings.exist_user, settings.exist_password)
        self.client = httpx.AsyncClient(auth=self.auth, timeout=20.0)

    async def get(self, collection: str, document_name: str) -> str:
        """
        Retrieves a document's content. Returns the content string on success.

        Raises:
            httpx.HTTPStatusError: If the database returns any 4xx or 5xx error,
                                including 404 Not Found.
        """
        document_url = f"{self.base_url}/{collection}/{document_name}"
        try:
            response = await self.client.get(document_url)
            # Let httpx raise an exception for any non-successful status code.
            response.raise_for_status()
            return response.text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in get(): {e.response.status_code}")
            # Re-raise the low-level exception for the service layer.
            raise

    async def put(self, collection: str, document_name: str, content: str) -> None:
        """
        Saves a document. Returns None on success.

        Raises:
            httpx.HTTPStatusError: If the database returns any 4xx or 5xx error.
        """

        try:
            # Ensure the collection exists first. This can also raise an httpx error.
            await self.create_collection(collection)

            document_url = f"{self.base_url}/{collection}/{document_name}"
            headers = {"Content-Type": "application/xml"}
            response = await self.client.put(
                document_url, content=content.encode("utf-8"), headers=headers
            )

            # Let httpx handle error conditions by raising an exception.
            response.raise_for_status()

            logger.info(f"Document '{document_name}' saved to '{collection}'.")

        except httpx.HTTPStatusError as e:
            # Log the specific technical error here.
            logger.error(
                f"HTTP error in put(): {e.response.status_code} - {e.response.text}")
            # Re-raise the original exception for the service layer to catch and interpret.
            raise

    async def delete(self, collection: str, document_name: str) -> None:
        """
        Deletes a document from ExistDB. Returns None on success.

        Raises:
            httpx.HTTPStatusError: If the database returns any 4xx or 5xx error,
                                including 404 Not Found.
        """
        document_url = f"{self.base_url}/{collection}/{document_name}"
        try:
            response = await self.client.delete(document_url)
            # Let httpx raise an exception for any non-successful status code.
            response.raise_for_status()
            logger.info(
                f"Document '{document_name}' deleted from '{collection}'.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in delete(): {e.response.status_code}")
            # Re-raise the low-level exception for the service layer to interpret.
            raise

    async def create_collection(self, collection_name: str) -> None:
        """
        Ensures a collection exists, creating it only if it is not already present.
        This method follows a "check, then act" pattern.
        """
        try:
            # Check if the collection already exists ---
            collection_is_present = await self._collection_exists(collection_name)

            # Act based on the check
            if not collection_is_present:
                # If the collection was not found, we proceed to create it.
                logger.info(
                    f"Collection '{collection_name}' not found, creating it.")
                headers = {"Content-Type": "application/xml"}
                content = '<collection xmlns="http://exist-db.org/collection-config/1.0"/>'

                response = await self.client.put(f"{self.base_url}/{collection_name}", content=content, headers=headers)
                response.raise_for_status()
                logger.info(
                    f"Collection '{collection_name}' created successfully.")
            else:
                # If the collection already exists, we do nothing.
                logger.info(
                    f"Collection '{collection_name}' already exists. Skipping creation.")

        except httpx.HTTPStatusError as e:
            # If any HTTP error occurs during the check or the creation, it's a real problem.
            logger.error(
                f"A database error occurred during collection setup for '{collection_name}': {e}")
            raise

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Deletes a collection and all its contents using an HTTP DELETE request.
        """
        collection_url = f"{self.base_url}/{collection_name}"
        try:
            response = await self.client.delete(collection_url)
            if response.status_code == 404:
                logger.warning(
                    f"Attempted to delete non-existent collection '{collection_name}'.")
                return False

            response.raise_for_status()
            logger.info(f"Collection '{collection_name}' deleted.")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error while deleting collection: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while deleting collection: {e}")
            raise

    async def query(self, xquery: str) -> str:
        """
        Executes an XQuery using an HTTP POST request and returns the raw XML result.
        """

        # ==========================================================
        # ADD THIS DEBUGGING BLOCK
        # ==========================================================
        print("\n" + "="*50)
        print("DEBUG: EXECUTING XQUERY FROM INSIDE THE 'query' METHOD")
        print(xquery)
        print("="*50 + "\n")
        # ==========================================================

        query_url = f"{self.base_url}/"
        headers = {"Content-Type": "application/xml"}
        # Wrap the user's query in the XML format required by the REST API
        content = f"""
        <query xmlns="http://exist.sourceforge.net/NS/exist">
            <text><![CDATA[{xquery}]]></text>
            <properties><property name="indent" value="yes"/></properties>
        </query>
        """
        try:
            response = await self.client.post(query_url, content=content.strip(), headers=headers)
            response.raise_for_status()
            logger.info(f"XQuery executed successfully.")
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error while executing query: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while querying: {e}")
            raise

    async def list_documents(self, collection: str) -> List[str]:
        """
        Retrieves a list of all document names within a collection.

        Returns:
            A list of document names on success.

        Raises:
            httpx.HTTPStatusError: If the database returns any 4xx or 5xx error.
            ET.XMLSyntaxError: If the response from the server is not well-formed XML.
        """
        collection_url = f"{self.base_url}/{collection}"
        try:
            response = await self.client.get(collection_url)

            # Let httpx raise an exception for any non-successful status code (including 404).
            response.raise_for_status()

            root = ET.fromstring(response.content)
            documents = root.xpath(LIST_DOCS_XPATH, namespaces=NS_MAP)
            return documents

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error listing documents for collection '{collection}': {e.response.status_code}")
            # Re-raise the low-level exception for the service layer to interpret.
            raise
        except ET.XMLSyntaxError as e:
            logger.error(
                f"Failed to parse XML response for collection '{collection}': {e}")
            # Re-raise for the service layer.
            raise

    async def exists(self, collection: str, document_name: str) -> bool:
        """
        Checks if a document exists in the database.

        Returns:
            True if the document exists, False otherwise.
        Raises:
            httpx.HTTPStatusError: For any non-404 HTTP error.
        """
        document_url = f"{self.base_url}/{collection}/{document_name}"
        try:
            response = await self.client.head(document_url)
            # HEAD is a lightweight request. A 2xx status means it exists.
            # A 404 will raise an exception, which we catch.
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            # If the error is a 404, it means the document doesn't exist. This is not an error for this check.
            if e.response.status_code == 404:
                return False
            # Any other error is a real problem, so we re-raise it.
            raise

    async def _collection_exists(self, collection_name: str) -> bool:
        """
        Private helper to check if a collection exists using a lightweight HEAD request.
        """
        try:
            response = await self.client.head(f"{self.base_url}/{collection_name}")
            response.raise_for_status()
            # A 2xx status means it exists.
            return True
        except httpx.HTTPStatusError as e:
            # A 404 status means it does not exist, which is a valid, non-exceptional case for this check.
            if e.response.status_code == 404:
                return False
            # Any other error (e.g., 401, 500) is an actual problem, so we re-raise the exception.
            raise
