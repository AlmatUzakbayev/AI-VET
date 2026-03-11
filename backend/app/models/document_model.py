from pydantic import BaseModel
from datetime import datetime


class DocumentMeta(BaseModel):
    id: str
    filename: str
    content_type: str
    uploaded_by: str
    uploaded_at: datetime
    chunk_count: int = 0

