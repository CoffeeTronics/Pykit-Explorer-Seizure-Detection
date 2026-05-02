import math
from ulab import numpy as np
from ulab.numpy import fft
from config import (
    FFT_SIZE, PAD_SIZE, SAMPLE_RATE,
    FALL_SPIKE_THRESHOLD, FALL_QUIET_THRESHOLD, FALL_QUIET_WINDOW,
    CLASS_STATIONARY, CLASS_LIGHT, CLASS_INTENSE, CLASS_SEIZURE, CLASS_FALL,
)


class Classifier:

    def classify(self, buffer):
        z_data     = np.array([s[2] for s in buffer], dtype=np.float)
        padding    = np.zeros(PAD_SIZE)
        padded     = np.concatenate((z_data, padding))
        real, imag = fft.fft(padded)
        spectrum   = np.sqrt(real * real + imag * imag)
        half       = FFT_SIZE // 2
        spectrum   = spectrum[:half]
        freqs      = np.linspace(0, SAMPLE_RATE / 2, half)

        e_stat  = self._band_energy(spectrum, freqs, 0, 1)
        e_light = self._band_energy(spectrum, freqs, 1, 2)
        e_int   = self._band_energy(spectrum, freqs, 2, 3)
        e_abn   = self._band_energy(spectrum, freqs, 4, 6)
        peak    = max(e_stat, e_light, e_int, e_abn)

        if peak == e_abn:
            return CLASS_FALL if self._looks_like_fall(buffer) else CLASS_SEIZURE
        elif peak == e_int:
            return CLASS_INTENSE
        elif peak == e_light:
            return CLASS_LIGHT
        else:
            return CLASS_STATIONARY

    def _band_energy(self, spectrum, freqs, lo, hi):
        energy = 0.0
        for i in range(len(freqs)):
            if lo <= freqs[i] < hi:
                energy += spectrum[i]
        return energy

    def _looks_like_fall(self, buffer):
        mags     = [self._magnitude(s[0], s[1], s[2]) for s in buffer]
        peak_idx = mags.index(max(mags))
        peak_val = mags[peak_idx]
        if peak_val < FALL_SPIKE_THRESHOLD:
            return False
        after_start  = min(peak_idx + 1, len(mags) - 1)
        after_end    = min(peak_idx + FALL_QUIET_WINDOW + 1, len(mags))
        after_window = mags[after_start:after_end]
        if len(after_window) == 0:
            return False
        return (sum(after_window) / len(after_window)) < FALL_QUIET_THRESHOLD

    @staticmethod
    def _magnitude(x, y, z):
        return math.sqrt(x * x + y * y + z * z)