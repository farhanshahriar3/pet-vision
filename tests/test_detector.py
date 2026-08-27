from app.detector import Detection


def test_detection_center():

    detection = Detection(
        class_name="dog",
        confidence=0.9,
        bbox=(100, 200, 300, 400),
    )

    assert detection.center == (
        200,
        300,
    )


def test_detection_dimensions():

    detection = Detection(
        class_name="cat",
        confidence=0.8,
        bbox=(100, 200, 300, 400),
    )

    assert detection.width == 200
    assert detection.height == 200