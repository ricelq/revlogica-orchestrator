# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/presentation/schema/manuscript.py

from pydantic import BaseModel


class ManuscriptBase(BaseModel):
    """
    Defines the expected JSON structure for a manuscript submission.
    """
    content: str  # The XML/TEI content as a string


class CreateDocumentRequest(ManuscriptBase):
    collection: str
    document_name: str
