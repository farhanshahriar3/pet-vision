from dataclasses import dataclass
from datetime import datetime


@dataclass
class TriggerEvent:
    timestamp: str
    animal: str
    confidence: float
    bbox: tuple[int, int, int, int]
    event: str = "virtual_trigger"


class VirtualTrigger:
    """
    Software-only trigger.

    This class deliberately does not control physical actuators.
    """

    def __init__(self, logger):
        self.logger = logger
        self.count = 0
        self.last_event: TriggerEvent | None = None

    def activate(
        self,
        animal: str,
        confidence: float,
        bbox: tuple[int, int, int, int],
    ) -> TriggerEvent:

        event = TriggerEvent(
            timestamp=datetime.now().isoformat(
                timespec="seconds"
            ),
            animal=animal,
            confidence=confidence,
            bbox=bbox,
        )

        self.count += 1
        self.last_event = event

        self.logger.info(
            "[VIRTUAL TRIGGER] %s detected | confidence=%.2f",
            animal,
            confidence,
        )

        return event