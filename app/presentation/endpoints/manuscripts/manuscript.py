# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/presentation/endpoints/manuscripts/manuscript.py

"""
API endpoints for manuscript ingestion and management.
"""
from fastapi import APIRouter, Depends, status, UploadFile, File, Response

from app.application.services.existdb_service import ExistDBService
from app.presentation.dependencies import get_existdb_service
from app.presentation.schema.manuscript import ManuscriptBase, CreateDocumentRequest


router = APIRouter()


@router.post(
    "/documents/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Create a document from a file upload",
    description="This endpoint creates a new document by uploading a file. It requires `collection` and `document_name` as parameters and a file to be uploaded. The file content is read and passed to the service layer for storage in ExistDB."
)
async def create_document_from_file(
    collection: str,
    document_name: str,
    file: UploadFile = File(...),
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Creates a new document from a file upload.
    Exceptions are handled by centralized handlers.
    """
    content = await file.read()

    await service.create_document(
        collection=collection,
        document_name=document_name,
        content=content.decode("utf-8")
    )

    return {"message": "Document uploaded successfully"}


@router.post(
    "/documents/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document from JSON",
    description="Creates a new document from a JSON payload."
)
async def create_document_from_json(
    request: CreateDocumentRequest,
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Creates a new document from a JSON payload.
    """
    await service.create_document(
        collection=request.collection,
        document_name=request.document_name,
        content=request.content
    )

    return {"message": "Document created successfully"}


@router.get(
    "/documents/list/{collection}",
    summary="List all documents in a collection",
    description="Provides a way to get a list of all documents within a specified collection. It's useful for browsing the contents of a collection without needing to know the specific document names."
)
async def list_documents(
    collection: str,
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Lists all documents within a given collection.
    Exceptions are handled by centralized handlers.
    """
    document_list = await service.list_documents_in_collection(collection=collection)
    return {"collection": collection, "documents": document_list}


@router.get(
    "/documents/{collection}/{document_name}",
    summary="Retrieve a single document",
    description="Retrieves a single document by its name from a specified collection. The `collection` and `document_name` are passed as URL parameters."
)
async def get_document(
    collection: str,
    document_name: str,
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Retrieves a single document.
    Exceptions are handled by centralized handlers.
    """
    document_content = await service.get_document(collection, document_name)

    return Response(content=document_content, media_type="application/xml")


@router.put(
    "/documents/{collection}/{document_name}",
    summary="Update an existing document",
    description="Updates an existing document with new content. The `collection` and `document_name` specify which document to modify, and the request body contains the new content to be saved."
)
async def update_document(
    collection: str,
    document_name: str,
    request: ManuscriptBase,  # Assuming ManuscriptBase is your Pydantic schema
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Updates an existing document with new content.
    Exceptions are handled by centralized handlers.
    """
    await service.update_document(
        collection=collection,
        document_name=document_name,
        new_content=request.content
    )

    return {"message": "Document updated successfully"}


@router.delete(
    "/documents/{collection}/{document_name}",
    summary="Delete a document",
    description="Deletes a single document. It uses the `collection` and `document_name` from the URL to identify and remove the document from the database."
)
async def delete_document(
    collection: str,
    document_name: str,
    service: ExistDBService = Depends(get_existdb_service)
):
    """
    Deletes a single document. 
    Exceptions are handled by centralized handlers.
    """
    await service.delete_document(collection=collection, document_name=document_name)

    return {"message": "Document deleted successfully"}
