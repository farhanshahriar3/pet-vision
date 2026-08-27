from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


@dataclass
class ModelConfig:
    name: str = "yolo11n.pt"
    device: str = "auto"
    inference_size: int = 640


@dataclass
class DetectionConfig:
    confidence_threshold: float = 0.60
    target_classes: list[str] = field(
        default_factory=lambda: ["dog", "cat"]
    )


@dataclass
class TriggerConfig:
    confirmation_time: float = 0.75
    cooldown: float = 5.0


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass
class SerialConfig:
    enabled: bool = False
    simulation_only: bool = True
    port: str = ""
    baudrate: int = 115200


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/pet_vision.log"


@dataclass
class DisplayConfig:
    show_boxes: bool = True
    show_confidence: bool = True
    show_fps: bool = True
    show_state: bool = True


@dataclass
class AppConfig:
    camera: CameraConfig
    model: ModelConfig
    detection: DetectionConfig
    trigger: TriggerConfig
    server: ServerConfig
    serial: SerialConfig
    logging: LoggingConfig
    display: DisplayConfig


def load_config(path: str = "config.yaml") -> AppConfig:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file) or {}

    camera = CameraConfig(**data.get("camera", {}))
    model = ModelConfig(**data.get("model", {}))
    detection = DetectionConfig(**data.get("detection", {}))
    trigger = TriggerConfig(**data.get("trigger", {}))
    server = ServerConfig(**data.get("server", {}))
    serial = SerialConfig(**data.get("serial", {}))
    logging_config = LoggingConfig(**data.get("logging", {}))
    display = DisplayConfig(**data.get("display", {}))

    validate_config(
        camera,
        model,
        detection,
        trigger,
        server,
        serial,
    )

    return AppConfig(
        camera=camera,
        model=model,
        detection=detection,
        trigger=trigger,
        server=server,
        serial=serial,
        logging=logging_config,
        display=display,
    )


def validate_config(
    camera: CameraConfig,
    model: ModelConfig,
    detection: DetectionConfig,
    trigger: TriggerConfig,
    server: ServerConfig,
    serial: SerialConfig,
) -> None:

    if camera.index < 0:
        raise ValueError("Camera index must be >= 0.")

    if camera.width <= 0 or camera.height <= 0:
        raise ValueError("Camera resolution must be positive.")

    if camera.fps <= 0:
        raise ValueError("Camera FPS must be positive.")

    if not 0.0 < detection.confidence_threshold <= 1.0:
        raise ValueError(
            "confidence_threshold must be between 0 and 1."
        )

    if trigger.confirmation_time < 0:
        raise ValueError("confirmation_time cannot be negative.")

    if trigger.cooldown < 0:
        raise ValueError("cooldown cannot be negative.")

    if server.port < 1 or server.port > 65535:
        raise ValueError("Server port must be between 1 and 65535.")

    if not detection.target_classes:
        raise ValueError("At least one target class is required.")

    if serial.enabled and not serial.simulation_only:
        raise ValueError(
            "Only simulation mode is supported by this project."
        )