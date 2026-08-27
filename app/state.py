from enum import Enum
import time


class VisionState(str, Enum):
    IDLE = "IDLE"
    DETECTED = "DETECTED"
    CONFIRMING = "CONFIRMING"
    TRIGGERED = "TRIGGERED"
    COOLDOWN = "COOLDOWN"


class DetectionStateMachine:
    def __init__(
        self,
        confirmation_time: float = 0.75,
        cooldown: float = 5.0,
    ):
        self.confirmation_time = confirmation_time
        self.cooldown_duration = cooldown

        self.state = VisionState.IDLE

        self.detection_started_at: float | None = None
        self.cooldown_started_at: float | None = None

        self.last_trigger_time: float | None = None

    def update(
        self,
        detected: bool,
        now: float | None = None,
    ) -> bool:

        now = now if now is not None else time.monotonic()

        if self.state == VisionState.COOLDOWN:
            if self.cooldown_remaining(now) <= 0:
                self.state = VisionState.IDLE
                self.cooldown_started_at = None

            else:
                return False

        if not detected:
            self.detection_started_at = None
            self.state = VisionState.IDLE
            return False

        if self.detection_started_at is None:
            self.detection_started_at = now
            self.state = VisionState.DETECTED
            return False

        elapsed = now - self.detection_started_at

        if elapsed < self.confirmation_time:
            self.state = VisionState.CONFIRMING
            return False

        self.state = VisionState.TRIGGERED
        self.last_trigger_time = now

        self.cooldown_started_at = now
        self.state = VisionState.COOLDOWN

        self.detection_started_at = None

        return True

    def confirmation_progress(
        self,
        now: float | None = None,
    ) -> float:

        now = now if now is not None else time.monotonic()

        if self.detection_started_at is None:
            return 0.0

        if self.confirmation_time <= 0:
            return 1.0

        elapsed = now - self.detection_started_at

        return max(
            0.0,
            min(1.0, elapsed / self.confirmation_time),
        )

    def cooldown_remaining(
        self,
        now: float | None = None,
    ) -> float:

        now = now if now is not None else time.monotonic()

        if self.cooldown_started_at is None:
            return 0.0

        remaining = (
            self.cooldown_duration
            - (now - self.cooldown_started_at)
        )

        return max(0.0, remaining)