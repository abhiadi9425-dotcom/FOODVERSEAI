import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.models.hygiene import HygieneReport, HygieneFinding
from app.schemas.hygiene import HygieneReportResponse, HygieneFindingResponse
from app.services.ai.provider_factory import get_ai_provider
from app.services.hygiene.video_processor import VideoProcessor
from app.utils.file_validation import validate_video_upload, save_upload_safely, VIDEO_MAX_SIZE

router = APIRouter(prefix="/hygiene", tags=["Kitchen Hygiene Monitoring"])


@router.post("/analyze", response_model=HygieneReportResponse)
async def analyze_hygiene_video(
    video: UploadFile = File(...),
    interval_seconds: Optional[float] = Form(2.0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Accepts kitchen video, samples keyframes using OpenCV at regular intervals,
    and runs vision model to evaluate glove usage, hair restraints, and surface contamination.
    """
    validate_video_upload(video)
    saved_path, _, relative_video_url = await save_upload_safely(
        video, max_bytes=VIDEO_MAX_SIZE, prefix="hygiene_vid"
    )

    frames_output_dir = os.path.join(settings.UPLOAD_DIR, "frames")
    os.makedirs(frames_output_dir, exist_ok=True)

    try:
        duration_s, extracted_frames = VideoProcessor.extract_keyframes(
            video_path=saved_path,
            output_dir=frames_output_dir,
            interval_seconds=interval_seconds or 2.0,
            max_frames=8,
            max_duration_s=float(settings.MAX_VIDEO_DURATION_SECONDS)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video processing failed: {str(e)}"
        )

    ai_provider = get_ai_provider()
    try:
        analysis_result = await ai_provider.analyze_hygiene_frames(extracted_frames)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hygiene visual analysis error: {str(e)}"
        )

    # Persist report if authenticated
    report_id = None
    created_at = None
    saved_findings = []

    if current_user:
        report = HygieneReport(
            user_id=current_user.id,
            video_url=relative_video_url,
            video_duration_s=round(duration_s, 1),
            total_frames_analyzed=len(extracted_frames),
            overall_summary=analysis_result.overall_summary,
            overall_risk_level=analysis_result.overall_risk_level,
            practical_recommendations=analysis_result.practical_recommendations,
            disclaimer=analysis_result.disclaimer
        )
        db.add(report)
        db.flush()
        report_id = report.id
        created_at = report.created_at

        # Match findings with extracted frame thumbnails
        for i, finding in enumerate(analysis_result.findings):
            matched_frame_url = None
            if i < len(extracted_frames):
                matched_frame_url = f"/uploads/frames/{extracted_frames[i]['frame_filename']}"
            elif extracted_frames:
                matched_frame_url = f"/uploads/frames/{extracted_frames[0]['frame_filename']}"

            db_finding = HygieneFinding(
                report_id=report.id,
                timestamp_s=finding.timestamp_s,
                category=finding.category,
                observation=finding.observation,
                severity=finding.severity,
                confidence=finding.confidence,
                frame_image_url=matched_frame_url
            )
            db.add(db_finding)
            saved_findings.append(db_finding)

        db.commit()
    else:
        # Construct ephemeral findings for preview
        for i, finding in enumerate(analysis_result.findings):
            frame_url = None
            if i < len(extracted_frames):
                frame_url = f"/uploads/frames/{extracted_frames[i]['frame_filename']}"
            saved_findings.append(HygieneFindingResponse(
                timestamp_s=finding.timestamp_s,
                category=finding.category,
                observation=finding.observation,
                severity=finding.severity,
                confidence=finding.confidence,
                frame_image_url=frame_url
            ))

    return HygieneReportResponse(
        id=report_id,
        video_url=relative_video_url,
        video_duration_s=round(duration_s, 1),
        total_frames_analyzed=len(extracted_frames),
        overall_summary=analysis_result.overall_summary,
        overall_risk_level=analysis_result.overall_risk_level,
        findings=[
            HygieneFindingResponse(
                id=getattr(f, "id", None),
                timestamp_s=f.timestamp_s,
                category=f.category,
                observation=f.observation,
                severity=f.severity,
                confidence=f.confidence,
                frame_image_url=f.frame_image_url
            )
            for f in saved_findings
        ],
        practical_recommendations=analysis_result.practical_recommendations,
        disclaimer=analysis_result.disclaimer,
        created_at=created_at
    )


@router.get("/history", response_model=List[HygieneReportResponse])
def get_hygiene_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(HygieneReport)\
        .filter(HygieneReport.user_id == current_user.id)\
        .order_by(HygieneReport.created_at.desc())\
        .all()
    return reports


@router.get("/reports/{report_id}", response_model=HygieneReportResponse)
def get_hygiene_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(HygieneReport)\
        .filter(HygieneReport.id == report_id, HygieneReport.user_id == current_user.id)\
        .first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hygiene report not found.")
    return report
