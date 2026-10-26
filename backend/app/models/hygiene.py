import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class HygieneReport(Base):
    __tablename__ = "hygiene_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    video_url = Column(String(500), nullable=False)
    video_duration_s = Column(Float, nullable=True)
    total_frames_analyzed = Column(Integer, default=0)
    
    overall_summary = Column(Text, nullable=False)
    overall_risk_level = Column(String(50), default="Moderate")  # Low, Moderate, High
    practical_recommendations = Column(JSON, default=list)
    disclaimer = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="hygiene_reports")
    findings = relationship("HygieneFinding", back_populates="report", cascade="all, delete-orphan")


class HygieneFinding(Base):
    __tablename__ = "hygiene_findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("hygiene_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    
    timestamp_s = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)  # Glove Usage, Hair Restraints, Cleanliness, Cross-contamination
    observation = Column(Text, nullable=False)
    severity = Column(String(50), default="Low")  # Low, Medium, High
    confidence = Column(Float, nullable=True)
    frame_image_url = Column(String(500), nullable=True)

    report = relationship("HygieneReport", back_populates="findings")
