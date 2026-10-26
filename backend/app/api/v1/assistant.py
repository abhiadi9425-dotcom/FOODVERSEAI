from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User, UserProfile
from app.models.assistant import Conversation, ConversationMessage
from app.schemas.assistant import AssistantChatRequest, MessageResponse, ConversationResponse
from app.services.ai.provider_factory import get_ai_provider
from app.utils.file_validation import validate_audio_upload, save_upload_safely, AUDIO_MAX_SIZE

router = APIRouter(prefix="/assistant", tags=["Multimodal AI Assistant"])


@router.post("/transcribe", response_model=dict)
async def transcribe_audio_file(
    audio: UploadFile = File(...)
):
    """
    Validates uploaded audio, transcribes speech-to-text via the active provider,
    and returns transcript for user preview or editing.
    """
    mime_type = validate_audio_upload(audio)
    _, audio_bytes, _ = await save_upload_safely(
        audio, max_bytes=AUDIO_MAX_SIZE, prefix="voice"
    )

    ai_provider = get_ai_provider()
    try:
        transcript = await ai_provider.transcribe_audio(audio_bytes, mime_type)
        return {
            "transcript": transcript,
            "mime_type": mime_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription error: {str(e)}"
        )


@router.post("/chat", response_model=dict)
async def chat_with_assistant(
    req: AssistantChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Multimodal assistant entry point. Routes context from food analyses, freshness,
    cooking, or user profile into conversational LLM reasoning.
    """
    convo = None
    if current_user:
        if req.conversation_id:
            convo = db.query(Conversation).filter(
                Conversation.id == req.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
        if not convo:
            title = req.message[:40] + ("..." if len(req.message) > 40 else "")
            convo = Conversation(user_id=current_user.id, title=title)
            db.add(convo)
            db.commit()
            db.refresh(convo)

    # Build context from user profile
    context_lines = [
        "You are FoodVerse AI, a friendly, authoritative multimodal food intelligence agent.",
        "Your role: provide science-backed nutrition guidance, culinary cooking tips, food safety advice, and meal planning.",
        "Crucial safety instruction: NEVER guarantee food is microbiologically safe from appearance alone. Treat user allergies as absolute safety exclusions."
    ]

    if current_user:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if profile:
            context_lines.append(f"User Profile: Diet={profile.dietary_pattern}, Allergies={profile.allergies}, Goal={profile.goal}, Cuisines={profile.cuisine_preferences}")

    if req.context_data:
        context_lines.append(f"Active Feature Context: {req.context_data}")

    # Build conversation messages
    history_messages = []
    if convo:
        past_msgs = db.query(ConversationMessage)\
            .filter(ConversationMessage.conversation_id == convo.id)\
            .order_by(ConversationMessage.created_at.asc())\
            .limit(10)\
            .all()
        for m in past_msgs:
            history_messages.append({"role": m.sender, "content": m.content})

    history_messages.append({"role": "user", "content": req.message})

    ai_provider = get_ai_provider()
    try:
        reply = await ai_provider.chat(
            messages=history_messages,
            context="\n".join(context_lines)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant chat error: {str(e)}"
        )

    # Persist messages if in authenticated conversation
    if convo:
        user_msg = ConversationMessage(
            conversation_id=convo.id,
            sender="user",
            content=req.message,
            modality=req.modality,
            metadata_json=req.context_data or {}
        )
        assistant_msg = ConversationMessage(
            conversation_id=convo.id,
            sender="assistant",
            content=reply,
            modality="text",
            metadata_json={}
        )
        db.add_all([user_msg, assistant_msg])
        db.commit()

    return {
        "reply": reply,
        "conversation_id": convo.id if convo else None
    }


@router.get("/conversations", response_model=List[dict])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convos = db.query(Conversation)\
        .filter(Conversation.user_id == current_user.id)\
        .order_by(Conversation.updated_at.desc())\
        .all()
    return [{"id": c.id, "title": c.title, "created_at": c.created_at, "updated_at": c.updated_at} for c in convos]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convo = db.query(Conversation)\
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)\
        .first()
    if not convo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return convo
