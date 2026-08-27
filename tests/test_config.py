from app.config import (
    CameraConfig,
    DetectionConfig,
    TriggerConfig,
    validate_config,
)


def test_valid_configuration():

    camera = CameraConfig()

    detection = DetectionConfig()

    trigger = TriggerConfig()

    validate_config(
        camera,
        type(
            "Model",
            (),
            {},
        )(),
        detection,
        trigger,
        type(
            "Server",
            (),
            {"port": 8000},
        )(),
        type(
            "Serial",
            (),
            {
                "enabled": False,
                "simulation_only": True,
            },
        )(),
    )


def test_invalid_confidence():

    camera = CameraConfig()

    detection = DetectionConfig(
        confidence_threshold=1.5
    )

    trigger = TriggerConfig()

    try:

        validate_config(
            camera,
            type("Model", (), {})(),
            detection,
            trigger,
            type(
                "Server",
                (),
                {"port": 8000},
            )(),
            type(
                "Serial",
                (),
                {
                    "enabled": False,
                    "simulation_only": True,
                },
            )(),
        )

        assert False

    except ValueError:

        assert True