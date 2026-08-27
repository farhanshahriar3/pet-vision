async function fetchStatus() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();

        document.getElementById("camera-status")
            .textContent =
            data.camera_connected
                ? "ONLINE"
                : "OFFLINE";

        document.getElementById("animal")
            .textContent =
            data.animal || "NONE";

        document.getElementById("confidence")
            .textContent =
            `${Math.round(data.confidence * 100)}%`;

        document.getElementById("state")
            .textContent =
            data.state;

        document.getElementById("cooldown")
            .textContent =
            data.cooldown_remaining.toFixed(1);

        document.getElementById("fps")
            .textContent =
            data.fps.toFixed(1);

        document.getElementById("frames")
            .textContent =
            data.frames_processed;

        document.getElementById("dogs")
            .textContent =
            data.dogs_detected;

        document.getElementById("cats")
            .textContent =
            data.cats_detected;

        document.getElementById("triggers")
            .textContent =
            data.trigger_count;

        document.getElementById("progress")
            .style.width =
            `${data.confirmation_progress * 100}%`;

        if (data.last_trigger) {

            const event =
                data.last_trigger;

            document.getElementById("last-trigger")
                .textContent =
                `${event.timestamp} — ` +
                `${event.animal.toUpperCase()} ` +
                `${Math.round(event.confidence * 100)}%`;
        }

    } catch (error) {

        console.error(
            "Status request failed:",
            error
        );
    }
}


async function startDetection() {

    await fetch(
        "/api/start",
        { method: "POST" }
    );
}


async function stopDetection() {

    await fetch(
        "/api/stop",
        { method: "POST" }
    );
}


async function resetStatistics() {

    await fetch(
        "/api/reset",
        { method: "POST" }
    );
}


async function testTrigger() {

    await fetch(
        "/api/test-trigger",
        { method: "POST" }
    );
}


setInterval(
    fetchStatus,
    250
);

fetchStatus();