from app.state import (
    DetectionStateMachine,
    VisionState,
)


def test_initial_state():

    machine = DetectionStateMachine(
        confirmation_time=1.0,
        cooldown=5.0,
    )

    assert machine.state == VisionState.IDLE


def test_detection_confirmation():

    machine = DetectionStateMachine(
        confirmation_time=1.0,
        cooldown=5.0,
    )

    assert not machine.update(
        detected=True,
        now=0.0,
    )

    assert machine.state == VisionState.DETECTED

    assert not machine.update(
        detected=True,
        now=0.5,
    )

    assert machine.state == VisionState.CONFIRMING

    assert machine.update(
        detected=True,
        now=1.1,
    )

    assert machine.state == VisionState.COOLDOWN


def test_detection_disappears():

    machine = DetectionStateMachine(
        confirmation_time=1.0,
        cooldown=5.0,
    )

    machine.update(
        detected=True,
        now=0.0,
    )

    machine.update(
        detected=False,
        now=0.2,
    )

    assert machine.state == VisionState.IDLE