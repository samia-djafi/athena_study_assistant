"""
Document endpoints for Athena (RAG UI Prototype — backend indexing not implemented).
Provides document cards, status updates, and upload validation for user-facing demonstrations.
"""
import uuid
import time
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.schemas import DocumentItem, DocumentStatus
from app.config import settings
from app.database.db import get_db_session, DBDocument

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents (UI Prototype)"])

# In-memory demo documents for clean prototype display
DEMO_DOCUMENTS = [
    DocumentItem(
        id="demo-doc-1",
        user_id="guest",
        filename="CS61B_Data_Structures_Lecture_08.pdf",
        file_type="application/pdf",
        size_bytes=2458120,
        status=DocumentStatus.READY,
        uploaded_at=time.time() - 86400,
        note="RAG UI prototype — backend indexing not implemented"
    ),
    DocumentItem(
        id="demo-doc-2",
        user_id="guest",
        filename="Transformer_Self_Attention_Paper.pdf",
        file_type="application/pdf",
        size_bytes=1048576,
        status=DocumentStatus.READY,
        uploaded_at=time.time() - 43200,
        note="RAG UI prototype — backend indexing not implemented"
    )
]

@router.get("", response_model=List[DocumentItem])
async def list_documents(user_id: str = "guest", db: AsyncSession = Depends(get_db_session)):
    """
    Returns documents list for the study materials UI prototype.
    """
    result = await db.execute(select(DBDocument).where(DBDocument.user_id == user_id))
    db_docs = result.scalars().all()
    
    if not db_docs:
        return DEMO_DOCUMENTS

    return [
        DocumentItem(
            id=d.id,
            user_id=d.user_id,
            filename=d.filename,
            file_type=d.file_type,
            size_bytes=d.size_bytes,
            status=DocumentStatus(d.status),
            uploaded_at=d.uploaded_at,
            note=d.note
        )
        for d in db_docs
    ]

@router.post("/upload", response_model=DocumentItem)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form("guest"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Handles file upload validation for the UI prototype.
    Validates file extension and size, then registers document status.
    (Note: As required by spec, does not chunk, embed, or index vectors).
    """
    # 1. Validate file type
    if file.content_type not in settings.ALLOWED_DOC_TYPES and not file.filename.endswith((".pdf", ".txt", ".md")):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file.content_type}'. Allowed types: PDF, TXT, Markdown."
        )

    # 2. Read contents to validate size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 3. Store in DB with UI Prototype disclaimer
    doc_id = str(uuid.uuid4())
    doc = DBDocument(
        id=doc_id,
        user_id=user_id,
        filename=file.filename,
        file_type=file.content_type or "application/octet-stream",
        size_bytes=len(contents),
        status=DocumentStatus.READY.value,
        uploaded_at=time.time(),
        note="RAG UI prototype — backend indexing not implemented"
    )
    db.add(doc)
    await db.commit()

    return DocumentItem(
        id=doc.id,
        user_id=doc.user_id,
        filename=doc.filename,
        file_type=doc.file_type,
        size_bytes=doc.size_bytes,
        status=DocumentStatus.READY,
        uploaded_at=doc.uploaded_at,
        note=doc.note
    )

@router.delete("/{document_id}")
async def delete_document(document_id: str, user_id: str = "guest", db: AsyncSession = Depends(get_db_session)):
    """Deletes a document from the user's study workspace."""
    result = await db.execute(select(DBDocument).where(DBDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if doc:
        if doc.user_id != user_id and user_id != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized to delete this document.")
        await db.delete(doc)
        await db.commit()
    return {"success": True, "message": f"Document {document_id} removed."}

@router.post("/{document_id}/reindex")
async def reindex_document(document_id: str):
    """
    Prototype re-index simulator for the interface.
    """
    return {
        "success": True,
        "document_id": document_id,
        "status": "Ready",
        "note": "RAG UI prototype — simulated reindexing complete"
    }
