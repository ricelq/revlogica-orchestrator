# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/presentation/schema/nlp.py

"""
Pydantic schemas for the NLP microservice communication.
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class NlpRequest(BaseModel):
    """
    Schema for the NLP microservice request body.
    """
    content: str = Field(...,
                         description="The text content to be analyzed.")


class NlpResponse(BaseModel):
    """
    Schema for the NLP microservice response body.
    This represents a single named entity.
    """
    text: str = Field(..., description="The text of the identified entity.")
    type: Literal["PERSON", "LOCATION", "CONCEPT"] = Field(
        ..., description="The type of the identified entity.")
    start_char: Optional[int] = Field(
        None, description="The starting character index of the entity.")
    end_char: Optional[int] = Field(
        None, description="The ending character index of the entity.")
