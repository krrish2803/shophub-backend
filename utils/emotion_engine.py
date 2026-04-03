"""
EmotionEngine - Lightweight version using DeepFace
"""
import base64
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


class EmotionEngine:
    def __init__(self):
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            from deepface import DeepFace
            self._deepface = DeepFace
            self._loaded = True
            logger.info("DeepFace loaded successfully.")
        except ImportError:
            logger.warning("DeepFace not installed. Using mock results.")

    def detect(self, image_b64: str) -> Dict[str, Any]:
        try:
            frame = self._decode_image(image_b64)
        except Exception as exc:
            return self._error(f"Image decode failed: {exc}")

        if not self._loaded:
            return self._mock_result()

        return self._run_deepface(frame)

    def _decode_image(self, image_b64: str) -> np.ndarray:
        import cv2
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Invalid image data.")
        return frame

    def _run_deepface(self, frame: np.ndarray) -> Dict[str, Any]:
        try:
            import cv2
            # Save temp image
            temp_path = "/tmp/temp_frame.jpg"
            cv2.imwrite(temp_path, frame)

            result = self._deepface.analyze(
                img_path=temp_path,
                actions=["emotion"],
                enforce_detection=False
            )

            if isinstance(result, list):
                result = result[0]

            emotions = result["emotion"]
            # Normalize to 0-1
            total = sum(emotions.values())
            normalized = {k: round(v/total, 4) for k, v in emotions.items()}
            dominant = max(normalized, key=normalized.get)

            return {
                "emotion":    dominant,
                "confidence": normalized[dominant],
                "all_scores": normalized,
                "error":      None,
            }

        except Exception as exc:
            logger.error(f"DeepFace error: {exc}")
            return self._mock_result()

    @staticmethod
    def _mock_result() -> Dict[str, Any]:
        import random
        emotion = random.choice(EMOTIONS)
        scores = {e: round(random.uniform(0.02, 0.15), 4) for e in EMOTIONS}
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
