"""
EmotionEngine
─────────────
Wraps OpenCV face detection + FER (Facial Emotion Recognition) library.
Accepts a base64-encoded image string from the frontend webcam frame
and returns the dominant emotion with confidence scores.

Dependencies:
    pip install fer opencv-python-headless numpy
"""
import base64
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

# FER emotions (in order returned by the library)
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


class EmotionEngine:
    def __init__(self):
        self._fer = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        """Lazy-load FER to avoid startup delay."""
        try:
            from fer import FER
            self._fer = FER(mtcnn=False)   # mtcnn=True for better accuracy (slower)
            self._loaded = True
            logger.info("FER model loaded successfully.")
        except ImportError:
            logger.warning(
                "FER library not installed. Run: pip install fer opencv-python-headless\n"
                "Emotion detection will return mock results."
            )
        except Exception as exc:
            logger.error(f"Failed to load FER model: {exc}")

    # ── Public API ──────────────────────────────────────────────────────────────
    def detect(self, image_b64: str) -> Dict[str, Any]:
        """
        Parameters
        ----------
        image_b64 : str
            Base64-encoded JPEG or PNG frame (with or without data-URI prefix).

        Returns
        -------
        dict with keys:
            emotion    : str   — dominant emotion label
            confidence : float — 0.0–1.0
            all_scores : dict  — {emotion: confidence, …}
            error      : str | None
        """
        try:
            frame = self._decode_image(image_b64)
        except Exception as exc:
            return self._error(f"Image decode failed: {exc}")

        if not self._loaded:
            return self._mock_result()

        return self._run_fer(frame)

    # ── Internal ────────────────────────────────────────────────────────────────
    def _decode_image(self, image_b64: str) -> np.ndarray:
        import cv2
        # Strip data-URI header if present (e.g. "data:image/jpeg;base64,...")
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        img_bytes = base64.b64decode(image_b64)
        nparr     = np.frombuffer(img_bytes, np.uint8)
        frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("cv2.imdecode returned None — invalid image data.")
        return frame

    def _run_fer(self, frame: np.ndarray) -> Dict[str, Any]:
        """Run FER on decoded frame."""
        try:
            results = self._fer.detect_emotions(frame)

            if not results:
                # No face detected — return neutral with low confidence
                return {
                    "emotion":    "neutral",
                    "confidence": 0.30,
                    "all_scores": {e: 0.0 for e in EMOTIONS},
                    "error":      None,
                }

            # Use the first (most prominent) face
            emotions: dict = results[0]["emotions"]
            dominant = max(emotions, key=emotions.get)
            confidence = emotions[dominant]

            return {
                "emotion":    dominant,
                "confidence": round(float(confidence), 4),
                "all_scores": {k: round(float(v), 4) for k, v in emotions.items()},
                "error":      None,
            }

        except Exception as exc:
            logger.error(f"FER inference error: {exc}")
            return self._error(str(exc))

    @staticmethod
    def _mock_result() -> Dict[str, Any]:
        """Fallback when FER is not available (dev mode / missing dep)."""
        import random
        emotion = random.choice(EMOTIONS)
        scores  = {e: round(random.uniform(0.02, 0.15), 4) for e in EMOTIONS}
        scores[emotion] = round(random.uniform(0.5, 0.9), 4)
        return {
            "emotion":    emotion,
            "confidence": scores[emotion],
            "all_scores": scores,
            "error":      None,
        }

    @staticmethod
    def _error(msg: str) -> Dict[str, Any]:
        return {
            "emotion":    None,
            "confidence": 0.0,
            "all_scores": {},
            "error":      msg,
        }
