# PyKit Seizure & Fall Detection

Based on: Zia et al., *"Detection of Motor Seizures and Falls in Mobile Application using Machine Learning Classifiers,"* IEEE IAICT 2020.

## Hardware

- **MCU:** SAME51J20A Curiosity Nano + PyKit Explorer Ruler Baseboard
- **Sensors:** IMU (accelerometer), NeoPixels, LCD, Class-D Audio, BLE (RNBD451)

## Pipeline

1. Sample IMU accelerometer at 50 Hz into a 2-second ring buffer (100 samples)
2. Every 2 seconds, run FFT on the buffer (padded to 128 for ulab requirement)
3. Sum spectral energy in four frequency bands to classify activity
4. Apply a fall-vs-seizure discriminator using time-domain spike detection
5. Drive NeoPixels, LCD, Class-D audio, and BLE alert based on classification result

## Frequency Band Classification

From Zia et al.:

| Band | Range | Activity |
|---|---|---|
| Stationary | 0–1 Hz | Sitting, desk work |
| Light ambulatory | 1–2 Hz | Walking, stairs |
| Intense ambulatory | 2–3 Hz | Jogging, running |
| Abnormal | 4–6 Hz | Motor seizure or fall |

## Fall Discriminator

Added heuristic — not in the original paper.

A fall produces a large transient spike followed by near-zero acceleration. A seizure produces sustained high-frequency oscillation. If peak magnitude exceeds `FALL_SPIKE_THRESHOLD` and the subsequent mean falls below `FALL_QUIET_THRESHOLD` within `FALL_QUIET_WINDOW` samples, the event is classified as **FALL** rather than **SEIZURE**.