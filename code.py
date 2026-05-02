# code.py - Seizure & Fall Detection for PyKit Explorer
# Based on: Zia et al., "Detection of Motor Seizures and Falls in Mobile
#           Application using Machine Learning Classifiers," IEEE IAICT 2020.
#
# Hardware: SAME51J20A Curiosity Nano + PyKit Explorer Ruler Baseboard
# Sensors:  IMU (accelerometer), NeoPixels, LCD, Class-D Audio, BLE (RNBD451)
#
# Pipeline:
#   1. Sample IMU accelerometer at 50 Hz into a 2-second ring buffer (100 samples)
#   2. Every 2 seconds, run FFT on the buffer (padded to 128 for ulab requirement)
#   3. Sum spectral energy in four frequency bands to classify activity
#   4. Apply a fall-vs-seizure discriminator using time-domain spike detection
#   5. Drive NeoPixels, LCD, Class-D audio, and BLE alert based on classification result
#
# Frequency band classification (from Zia et al.):
#   Stationary         0-1 Hz  (sitting, desk work)
#   Light ambulatory   1-2 Hz  (walking, stairs)
#   Intense ambulatory 2-3 Hz  (jogging, running)
#   Abnormal           4-6 Hz  (motor seizure or fall)
#
# Fall discriminator (added heuristic, not in original paper):
#   A fall produces a large transient spike followed by near-zero acceleration.
#   A seizure produces sustained high-frequency oscillation.
#   If peak magnitude > FALL_SPIKE_THRESHOLD and subsequent mean < FALL_QUIET_THRESHOLD
#   within FALL_QUIET_WINDOW samples, classify as FALL rather than SEIZURE.

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