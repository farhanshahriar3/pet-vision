from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

import cv2
import time


def create_app(controller):
    app = FastAPI(
        title="Pet Vision"
    )

    templates = Jinja2Templates(
        directory="web/templates"
    )

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "status": controller.get_status()
            },
        )

    @app.get("/api/status")
    async def status():
        return controller.get_status()

    @app.post("/api/trigger-test")
    async def trigger_test():
        controller.test_virtual_trigger()

        return {
            "success": True,
            "message": "Virtual trigger activated",
        }

    @app.post("/api/reset")
    async def reset():
        controller.reset_statistics()

        return {
            "success": True
        }

    @app.post("/api/detection/toggle")
    async def toggle_detection():
        controller.detection_enabled = (
            not controller.detection_enabled
        )

        return {
            "success": True,
            "enabled": (
                controller.detection_enabled
            ),
        }

    @app.get("/video")
    async def video():

        async def generate():

            while controller.running:

                frame = (
                    controller.get_processed_frame()
                )

                if frame is None:
                    await _async_sleep(0.03)
                    continue

                success, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        85,
                    ],
                )

                if not success:
                    await _async_sleep(0.03)
                    continue

                jpeg = encoded.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + jpeg
                    + b"\r\n"
                )

                await _async_sleep(0.03)

        return StreamingResponse(
            generate(),
            media_type=(
                "multipart/x-mixed-replace; "
                "boundary=frame"
            ),
        )

    return app


async def _async_sleep(seconds):
    """
    Small async sleep helper.
    """
    import asyncio

    await asyncio.sleep(seconds)