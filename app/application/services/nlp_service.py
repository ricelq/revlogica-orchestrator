# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/application/services/nlp_service.py

"""
Service for interacting with the NLP Microservice.
"""
import httpx
from ..infrastructure.config import settings
from ...domain.exceptions import ExistDBError, NLPServiceError
from ..schemas.nlp import NlpRequest, NlpResponse
from typing import List


class NlpService:
    """
    Handles communication with the NLP microservice to extract entities from text.
    """

    def __init__(self):
        """
        Initializes the service with the base URL for the NLP microservice API.
        """
        self.base_url = settings.nlp_service_url
        self.client = httpx.AsyncClient()

    async def extract_entities(self, text_content: str) -> List[NlpResponse]:
        """
        Sends text to the NLP microservice for Named Entity Recognition.

        Args:
            text_content: The plain text content of the manuscript.

        Returns:
            A list of structured entities extracted from the text.

        Raises:
            NLPServiceError: If the NLP microservice call fails.
        """
        endpoint = f"{self.base_url}/extract-entities"
        request_data = NlpRequest(text_content=text_content)

        try:
            response = await self.client.post(endpoint, json=request_data.model_dump_json())
            response.raise_for_status()

            # Assuming the response is a list of dictionaries that match NlpResponse schema
            return [NlpResponse(**item) for item in response.json()]

        except httpx.HTTPStatusError as exc:
            raise NLPServiceError(
                message=f"Failed to extract entities: {exc.response.text}",
                status_code=exc.response.status_code
            )
        except httpx.RequestError as exc:
            raise NLPServiceError(
                message=f"An error occurred while communicating with the NLP service: {exc}",
                status_code=500
            )
