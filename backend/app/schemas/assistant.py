from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class AssistantChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    modality: str = "text"  # text, audio, image, video
    context_data: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sender: str
    content: str
    modality: str
    metadata_json: Dict[str, Any] = {}
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
