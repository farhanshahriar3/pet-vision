
import argparse
import threading
import time

import cv2
import uvicorn

from app.config import load_config
from app.detector import AnimalDetector
from app.logger import setup_logging
from app.metrics import Metrics
from app.state import DetectionStateMachine, VisionState
from app.trigger import VirtualTrigger
from app.video_source import create_video_source
from web.server import create_app


class PetVisionController:
    def __init__(
        self,
        config,
        logger,
        source_type="camera",
        source_path=None,
    ):
        self.config = config
        self.logger = logger
        self.source_type = source_type

        # Create camera, video-file, or image source.
        self.source = create_video_source(
            source_type=source_type,
            path=source_path,
            camera_index=config.camera.index,
            width=config.camera.width,
            height=config.camera.height,
            fps=config.camera.fps,
        )

        # YOLO detector.
        self.detector = AnimalDetector(
            model_name=config.model.name,
            confidence_threshold=(
                config.detection.confidence_threshold
            ),
            target_classes=(
                config.detection.target_classes
            ),
            device=config.model.device,
            inference_size=config.model.inference_size,
        )

        # Detection confirmation/cooldown state machine.
        self.state_machine = DetectionStateMachine(
            confirmation_time=(
                config.trigger.confirmation_time
            ),
            cooldown=config.trigger.cooldown,
        )

        # Safe software-only trigger.
        self.trigger = VirtualTrigger(logger)

        # Statistics.
        self.metrics = Metrics()

        # Runtime state.
        self.running = False
        self.detection_enabled = True

        self.latest_processed_frame = None
        self.latest_detections = []
        self.latest_animal = None
        self.latest_confidence = 0.0

        self.last_trigger_flash_until = 0.0

        self._frame_lock = threading.Lock()
        self.processing_thread = None

    # ======================================================
    # START
    # ======================================================

    def start(self):
        self.logger.info("Starting Pet Vision.")
        self.logger.info(
            "Input source: %s",
            self.source_type,
        )

        self.source.start()

        self.running = True

        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
        )

        self.processing_thread.start()

        self.logger.info(
            "Vision processing started."
        )

    # ======================================================
    # MAIN PROCESSING LOOP
    # ======================================================

    def _processing_loop(self):
        while self.running:
            frame = self.source.get_frame()

            if frame is None:
                if not self.source.running:
                    self.logger.info(
                        "Input source stopped."
                    )
                    break

                time.sleep(0.03)
                continue

            try:
                self._process_frame(frame)

            except Exception as exc:
                self.logger.exception(
                    "Frame processing error: %s",
                    exc,
                )

                time.sleep(0.1)

    # ======================================================
    # PROCESS FRAME
    # ======================================================

    def _process_frame(self, frame):
        detections = []

        if self.detection_enabled:
            detections = self.detector.detect(frame)

        self.latest_detections = detections

        self.metrics.update(detections)

        # Find strongest animal detection.
        if detections:
            best = max(
                detections,
                key=lambda detection: detection.confidence,
            )

            self.latest_animal = best.class_name
            self.latest_confidence = best.confidence

        else:
            self.latest_animal = None
            self.latest_confidence = 0.0

        # --------------------------------------------------
        # STATE MACHINE
        # --------------------------------------------------

        animal_detected = bool(detections)

        trigger_event = self.state_machine.update(
            detected=animal_detected
        )

        # --------------------------------------------------
        # VIRTUAL TRIGGER
        # --------------------------------------------------

        if trigger_event and detections:
            best = max(
                detections,
                key=lambda detection: detection.confidence,
            )

            self.trigger.activate(
                animal=best.class_name,
                confidence=best.confidence,
                bbox=best.bbox,
            )

            self.last_trigger_flash_until = (
                time.monotonic() + 1.0
            )

        # --------------------------------------------------
        # DRAW DETECTIONS
        # --------------------------------------------------

        output = self.detector.draw(
            frame,
            detections,
            show_boxes=self.config.display.show_boxes,
            show_confidence=(
                self.config.display.show_confidence
            ),
        )

        self._draw_interface(output)

        with self._frame_lock:
            self.latest_processed_frame = output

    # ======================================================
    # DRAW UI
    # ======================================================

    def _draw_interface(self, frame):
        overlay_height = 190

        cv2.rectangle(
            frame,
            (0, 0),
            (430, overlay_height),
            (20, 20, 20),
            -1,
        )

        cv2.putText(
            frame,
            "PET VISION",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"Source: {self.source_type.upper()}",
            (15, 57),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (180, 180, 255),
            2,
            cv2.LINE_AA,
        )

        status = (
            "ONLINE"
            if self.source.connected
            else "OFFLINE"
        )

        status_color = (
            (100, 255, 100)
            if self.source.connected
            else (80, 80, 255)
        )

        cv2.putText(
            frame,
            f"Source: {status}",
            (15, 84),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            status_color,
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"FPS: {self.metrics.fps:.1f}",
            (15, 111),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"State: {self.state_machine.state.value}",
            (15, 138),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 220, 100),
            2,
            cv2.LINE_AA,
        )

        # Confirmation progress.
        progress = (
            self.state_machine.confirmation_progress()
        )

        if (
            self.state_machine.state
            == VisionState.CONFIRMING
        ):
            bar_x = 15
            bar_y = 155
            bar_width = 280
            bar_height = 10

            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (
                    bar_x + bar_width,
                    bar_y + bar_height,
                ),
                (70, 70, 70),
                -1,
            )

            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (
                    bar_x
                    + int(bar_width * progress),
                    bar_y + bar_height,
                ),
                (50, 220, 100),
                -1,
            )

            cv2.putText(
                frame,
                "CONFIRMING",
                (305, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (50, 220, 100),
                1,
                cv2.LINE_AA,
            )

        # Cooldown display.
        if (
            self.state_machine.state
            == VisionState.COOLDOWN
        ):
            remaining = (
                self.state_machine.cooldown_remaining()
            )

            cv2.putText(
                frame,
                f"COOLDOWN: {remaining:.1f}s",
                (15, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 180, 255),
                2,
                cv2.LINE_AA,
            )

        # Virtual trigger notification.
        if (
            time.monotonic()
            < self.last_trigger_flash_until
        ):
            height, width = frame.shape[:2]

            cv2.rectangle(
                frame,
                (0, 0),
                (width - 1, height - 1),
                (0, 255, 100),
                8,
            )

            cv2.putText(
                frame,
                "VIRTUAL TRIGGER ACTIVATED",
                (30, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 100),
                3,
                cv2.LINE_AA,
            )

    # ======================================================
    # GET CURRENT FRAME
    # ======================================================

    def get_processed_frame(self):
        with self._frame_lock:
            if self.latest_processed_frame is None:
                return None

            return self.latest_processed_frame.copy()

    # ======================================================
    # STATUS
    # ======================================================

    def get_status(self):
        last_event = self.trigger.last_event

        return {
            "running": self.running,
            "source_type": self.source_type,
            "detection_enabled": self.detection_enabled,
            "camera_connected": self.source.connected,
            "animal": self.latest_animal,
            "confidence": self.latest_confidence,
            "state": self.state_machine.state.value,
            "confirmation_progress": (
                self.state_machine.confirmation_progress()
            ),
            "cooldown_remaining": (
                self.state_machine.cooldown_remaining()
            ),
            "fps": self.metrics.fps,
            "frames_processed": (
                self.metrics.frames_processed
            ),
            "dogs_detected": (
                self.metrics.dogs_detected
            ),
            "cats_detected": (
                self.metrics.cats_detected
            ),
            "total_detections": (
                self.metrics.total_detections
            ),
            "trigger_count": self.trigger.count,
            "last_trigger": (
                {
                    "timestamp": last_event.timestamp,
                    "animal": last_event.animal,
                    "confidence": last_event.confidence,
                    "bbox": last_event.bbox,
                }
                if last_event
                else None
            ),
        }

    # ======================================================
    # RESET STATISTICS
    # ======================================================

    def reset_statistics(self):
        self.metrics = Metrics()

        self.trigger.count = 0
        self.trigger.last_event = None

        self.logger.info(
            "Statistics reset."
        )

    # ======================================================
    # TEST VIRTUAL TRIGGER
    # ======================================================

    def test_virtual_trigger(self):
        self.trigger.activate(
            animal="test",
            confidence=1.0,
            bbox=(0, 0, 0, 0),
        )

        self.last_trigger_flash_until = (
            time.monotonic() + 1.0
        )

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):
        if not self.running:
            return

        self.logger.info(
            "Stopping Pet Vision."
        )

        self.running = False

        if self.processing_thread:
            self.processing_thread.join(
                timeout=2.0
            )

        self.source.stop()

        self.logger.info(
            "Shutdown complete."
        )


# ==========================================================
# ARGUMENTS
# ==========================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Pet Vision dog/cat "
            "computer vision system."
        )
    )

    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file.",
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Camera index.",
    )

    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to an image file.",
    )

    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to a video file.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run software-only test.",
    )

    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Disable web dashboard.",
    )

    args = parser.parse_args()

    # Only one input source may be selected.
    source_arguments = sum(
        value is not None
        for value in [
            args.camera,
            args.image,
            args.video,
        ]
    )

    if source_arguments > 1:
        parser.error(
            "Use only one of "
            "--camera, --image, or --video."
        )

    return args


# ==========================================================
# MAIN
# ==========================================================

def main():
    args = parse_args()

    config = load_config(
        args.config
    )

    if args.camera is not None:
        config.camera.index = args.camera

    if args.debug:
        config.logging.level = "DEBUG"

    logger = setup_logging(
        level=config.logging.level,
        log_file=config.logging.file,
    )

    controller = None

    try:

        # --------------------------------------------------
        # SOFTWARE TEST
        # --------------------------------------------------

        if args.test:
            logger.info(
                "Running software test mode."
            )

            trigger = VirtualTrigger(
                logger
            )

            trigger.activate(
                animal="test",
                confidence=1.0,
                bbox=(0, 0, 0, 0),
            )

            print(
                "\nTest completed successfully."
            )

            return

        # --------------------------------------------------
        # SELECT SOURCE
        # --------------------------------------------------

        if args.image:
            source_type = "image"
            source_path = args.image

        elif args.video:
            source_type = "video"
            source_path = args.video

        else:
            source_type = "camera"
            source_path = None

        # --------------------------------------------------
        # CREATE CONTROLLER
        # --------------------------------------------------

        controller = PetVisionController(
            config=config,
            logger=logger,
            source_type=source_type,
            source_path=source_path,
        )

        controller.start()

        # --------------------------------------------------
        # NO WEB
        # --------------------------------------------------

        if args.no_web:
            logger.info(
                "Web dashboard disabled."
            )

            while True:
                time.sleep(1)

        # --------------------------------------------------
        # WEB DASHBOARD
        # --------------------------------------------------

        app = create_app(
            controller
        )

        server_config = uvicorn.Config(
            app,
            host=config.server.host,
            port=config.server.port,
            log_level="info",
        )

        server = uvicorn.Server(
            server_config
        )

        logger.info(
            "Dashboard available at "
            f"http://"
            f"{config.server.host}:"
            f"{config.server.port}"
        )

        server.run()

    except KeyboardInterrupt:
        logger.info(
            "Keyboard interrupt received."
        )

    finally:
        if controller:
            controller.stop()


if __name__ == "__main__":
    main()

