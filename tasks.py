import asyncio
import time
from config import SAMPLE_RATE, WINDOW_SIZE, CLASS_SEIZURE, CLASS_FALL, COLORS


async def task_sampler(imu, ring_buffer, buffer_lock):
    interval = 1.0 / SAMPLE_RATE
    while True:
        x, y, z = imu.acceleration
        async with buffer_lock:
            ring_buffer.append((x, y, z))
            if len(ring_buffer) > WINDOW_SIZE:
                ring_buffer.pop(0)
        await asyncio.sleep(interval)


async def task_classifier(ring_buffer, buffer_lock, state, classifier):
    while True:
        await asyncio.sleep(2.0)
        async with buffer_lock:
            if len(ring_buffer) < WINDOW_SIZE:
                continue
            snapshot = list(ring_buffer)
        result                 = classifier.classify(snapshot)
        state["current_class"] = result
        state["alert_active"]  = result in (CLASS_SEIZURE, CLASS_FALL)
        print(f"[{time.monotonic():.1f}s] Classification: {result}")


async def task_output(pixels, state, output_manager):
    while True:
        output_manager.poll_ble()

        activity_class = state["current_class"]
        alert_active   = state["alert_active"]
        color          = COLORS.get(activity_class, (255, 255, 255))

        if alert_active:
            pixels.fill(color)
            pixels.show()
            await asyncio.sleep(0.1)
            pixels.fill((0, 0, 0))
            pixels.show()
            await asyncio.sleep(0.1)
        else:
            pixels.fill(color)
            pixels.show()
            await asyncio.sleep(0.25)

        output_manager.update_lcd(activity_class)
        output_manager.update_audio(activity_class)

        if alert_active:
            output_manager.send_ble_alert(activity_class)