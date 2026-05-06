"""
AlgoTrade Engine — FFT Cycle Detection
Extracts dominant frequency components from price time series.

DAA Paradigm: Transform (Fast Fourier Transform)
Brute-force: O(n²) DFT  |  Optimized: O(n log n) FFT via scipy.fft
"""

import numpy as np
from scipy.fft import fft as scipy_fft
from config import TOP_K_FREQUENCIES


def dft_brute(signal: np.ndarray) -> np.ndarray:
    """DFT — O(n²) direct computation."""
    N = len(signal)
    X = np.zeros(N, dtype=complex)
    for k in range(N):
        for n in range(N):
            X[k] += signal[n] * np.exp(-2j * np.pi * k * n / N)
    return X


def fft_optimized(signal: np.ndarray) -> np.ndarray:
    """FFT via scipy — O(n log n) Cooley-Tukey."""
    return scipy_fft(signal)


def extract_cycles(prices: np.ndarray, top_k: int = TOP_K_FREQUENCIES, use_optimized: bool = True) -> dict:
    """Extract dominant trading cycles from price series."""
    N = len(prices)
    x = np.arange(N)
    trend = np.polyval(np.polyfit(x, prices, 1), x)
    detrended = (prices - trend) * np.hanning(N)

    spectrum = fft_optimized(detrended) if use_optimized else dft_brute(detrended)
    power = np.abs(spectrum[:N // 2]) ** 2
    freqs = np.arange(N // 2) / N

    min_idx, max_idx = max(1, N // (N // 2)), min(N // 2, N // 3)
    valid_power = power[min_idx:max_idx]
    valid_freqs = freqs[min_idx:max_idx]

    if len(valid_power) == 0:
        return {"frequencies": [], "periods": [], "amplitudes": [], "spectrum": power.tolist()}

    top_indices = np.argsort(valid_power)[-top_k:][::-1]
    dominant_freqs = valid_freqs[top_indices].tolist()
    periods = [round(1.0 / f, 1) if f > 0 else 0 for f in dominant_freqs]
    amplitudes = valid_power[top_indices].tolist()

    labels = []
    for p in periods:
        if p <= 7: labels.append("Weekly")
        elif p <= 25: labels.append("Monthly")
        elif p <= 70: labels.append("Quarterly")
        else: labels.append("Annual")

    return {
        "frequencies": dominant_freqs, "periods": periods,
        "amplitudes": amplitudes, "cycle_labels": labels,
        "spectrum": {"power": power.tolist(), "frequencies": freqs.tolist()},
    }
