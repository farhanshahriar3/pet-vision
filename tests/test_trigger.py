from app.trigger import VirtualTrigger


class FakeLogger:

    def info(self, *args, **kwargs):
        pass


def test_virtual_trigger():

    trigger = VirtualTrigger(
        logger=FakeLogger()
    )

    event = trigger.activate(
        animal="dog",
        confidence=0.91,
        bbox=(10, 20, 100, 200),
    )

    assert trigger.count == 1

    assert event.animal == "dog"

    assert event.confidence == 0.91

    assert event.event == "virtual_trigger"