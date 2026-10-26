import os
import uuid
import logging
from typing import List, Dict, Any, Tuple
import cv2

logger = logging.getLogger(__name__)


class VideoProcessor:
    @staticmethod
    def extract_keyframes(
        video_path: str,
        output_dir: str,
        interval_seconds: float = 2.0,
        max_frames: int = 10,
        max_duration_s: float = 120.0
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Extracts key frames from a video file at given second intervals using OpenCV.
        Saves JPEG thumbnails to output_dir and returns video duration and frames list.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file. Format may be unsupported or corrupted.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        if fps <= 0 or total_frames <= 0:
            cap.release()
            raise ValueError("Invalid video stream or zero frame count detected.")

        duration_s = total_frames / fps
        if duration_s > max_duration_s:
            logger.warning(f"Video duration {duration_s:.1f}s exceeds limit {max_duration_s}s. Processing first {max_duration_s}s.")
            duration_s = max_duration_s

        os.makedirs(output_dir, exist_ok=True)
        extracted_frames: List[Dict[str, Any]] = []

        step_frames = int(fps * interval_seconds)
        if step_frames <= 0:
            step_frames = 30

        current_frame_idx = 0
        while cap.isOpened() and len(extracted_frames) < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            timestamp_s = round(current_frame_idx / fps, 2)
            if timestamp_s > duration_s:
                break

            # Resize frame if overly large to optimize processing and storage
            height, width = frame.shape[:2]
            if width > 1280:
                scale = 1280 / width
                frame = cv2.resize(frame, (1280, int(height * scale)), interpolation=cv2.INTER_AREA)

            # Encode frame to JPEG
            success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if success:
                frame_bytes = buffer.tobytes()
                frame_filename = f"frame_{uuid.uuid4().hex[:8]}_{int(timestamp_s * 10)}.jpg"
                frame_filepath = os.path.join(output_dir, frame_filename)
                
                with open(frame_filepath, "wb") as f_out:
                    f_out.write(frame_bytes)

                extracted_frames.append({
                    "timestamp_s": timestamp_s,
                    "frame_filename": frame_filename,
                    "frame_filepath": frame_filepath,
                    "image_bytes": frame_bytes
                })

            current_frame_idx += step_frames

        cap.release()
        return duration_s, extracted_frames
