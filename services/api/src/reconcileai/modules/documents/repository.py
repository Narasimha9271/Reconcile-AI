from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from reconcileai.modules.documents.service import StoredDocument


class DocumentRepository:
    def create(self, session: Session, document: StoredDocument) -> None:
        try:
            session.execute(text("""
                INSERT INTO documents (id, organization_id, document_type, original_filename, content_type, byte_size, sha256, storage_key, status)
                VALUES (:id, :organization_id, :document_type, :original_filename, :content_type, :byte_size, :sha256, :storage_key, :status)
            """), document.__dict__)
        except IntegrityError as error:
            if getattr(error.orig, "sqlstate", None) == "23505":
                raise ValueError("Duplicate document for this organization.") from error
            raise

    def list_for_tenant(self, session: Session) -> list[StoredDocument]:
        rows = session.execute(text("""
            SELECT id, organization_id, document_type, original_filename, content_type, byte_size, sha256, storage_key, status
            FROM documents ORDER BY created_at DESC, id
        """)).mappings().all()
        return [StoredDocument(**{key: str(value) if key in {"id", "organization_id"} else value for key, value in row.items()}) for row in rows]
