import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_BYTES = 10 * 1024 * 1024

@dataclass(frozen=True)
class StoredDocument:
    id: str
    organization_id: str
    document_type: str
    original_filename: str
    content_type: str
    byte_size: int
    sha256: str
    storage_key: str
    status: str

class LocalDocumentStore:
    """Development adapter. Production replaces this with private S3 + malware scanning."""
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    async def save(self, organization_id: UUID, document_type: str, upload: UploadFile) -> StoredDocument:
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF, PNG, and JPEG uploads are supported.")
        content = await upload.read(MAX_BYTES + 1)
        if not content:
            raise HTTPException(status_code=422, detail="Uploaded file is empty.")
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="Uploaded file exceeds the 10 MiB limit.")
        digest = hashlib.sha256(content).hexdigest()
        document_id = str(uuid4())
        suffix = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg"}[upload.content_type]
        key = f"org/{organization_id}/documents/{document_id}/original{suffix}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        document = StoredDocument(document_id, str(organization_id), document_type, upload.filename or "upload", upload.content_type, len(content), digest, key, "QUEUED")
        return document
