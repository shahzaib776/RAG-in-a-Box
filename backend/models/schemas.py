from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    chunks_processed: int
    message: str