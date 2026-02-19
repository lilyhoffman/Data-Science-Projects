from dataclasses import dataclass
from typing import Optional, List


@dataclass
class FacePresenceEvent:
    event: str  # "FOUND" or "LOST"
    timestamp_ms: int
    duration_ms: Optional[int] = None


class FacePresenceTracker:
    """
    Debounced face presence state machine.
    - FOUND after N consecutive frames with face >= threshold
    - LOST  after M consecutive frames without face >= threshold
    """
    def __init__(self, found_after: int = 3, lost_after: int = 10, score_threshold: float = 0.5):
        self.found_after = found_after
        self.lost_after = lost_after
        self.score_threshold = score_threshold

        self.present = False
        self._hit_streak = 0
        self._miss_streak = 0
        self._session_start_ms: Optional[int] = None

    def _has_valid_face(self, detections) -> bool:
        if not detections:
            return False
        for det in detections:
            if det.categories and det.categories[0].score >= self.score_threshold:
                return True
        return False

    def update(self, detections, timestamp_ms: int) -> List[FacePresenceEvent]:
        events: List[FacePresenceEvent] = []

        has_face = self._has_valid_face(detections)

        if has_face:
            self._hit_streak += 1
            self._miss_streak = 0
        else:
            self._miss_streak += 1
            self._hit_streak = 0

        if (not self.present) and (self._hit_streak >= self.found_after):
            self.present = True
            self._session_start_ms = timestamp_ms
            events.append(FacePresenceEvent("FOUND", timestamp_ms))

        elif self.present and (self._miss_streak >= self.lost_after):
            self.present = False
            duration = None
            if self._session_start_ms is not None:
                duration = max(0, timestamp_ms - self._session_start_ms)
            self._session_start_ms = None
            events.append(FacePresenceEvent("LOST", timestamp_ms, duration_ms=duration))

        return events
