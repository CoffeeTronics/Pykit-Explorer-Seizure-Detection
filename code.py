import pykit_explorer
import asyncio
from config import SAMPLE_RATE, WINDOW_SIZE, FFT_SIZE
from hardware import init_hardware
from classifier import Classifier
from output import OutputManager
from tasks import task_sampler, task_classifier, task_output


async def main():
    pixels, imu, lcd, audio, ble = init_hardware()
    classifier = Classifier()
    output     = OutputManager(lcd, audio, ble)

    ring_buffer = []
    buffer_lock = asyncio.Lock()
    state       = {"current_class": "STATIONARY", "alert_active": False}

    print("PyKit Explorer -- Seizure & Fall Detection")
    print("  Sample rate :", SAMPLE_RATE, "Hz")
    print("  Window size :", WINDOW_SIZE, "samples (", WINDOW_SIZE / SAMPLE_RATE, "s)")
    print("  FFT size    :", FFT_SIZE)
    print("  Audio       :", "enabled" if audio is not None else "not available")
    print("  BLE         :", "enabled (RNBD451)" if ble is not None else "not available")
    print("  Display     : enabled (ST7789 240x135)")
    print("Starting tasks...")

    await asyncio.gather(
        task_sampler(imu, ring_buffer, buffer_lock),
        task_classifier(ring_buffer, buffer_lock, state, classifier),
        task_output(pixels, state, output),
    )


asyncio.run(main())