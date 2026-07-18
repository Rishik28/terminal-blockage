"""Render development audio assets for Terminal Blockage."""

from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro


ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "tools" / "voice"
OUT_DIR = ROOT / "src" / "assets" / "audio"
SAMPLE_RATE = 24_000


def normalize(samples: np.ndarray, peak: float = 0.92) -> np.ndarray:
    samples = np.asarray(samples, dtype=np.float32)
    samples -= np.mean(samples)
    maximum = np.max(np.abs(samples)) or 1.0
    return np.tanh(samples / maximum * 1.8) / np.tanh(1.8) * peak


def render_voices() -> None:
    kokoro = Kokoro(VOICE_DIR / "kokoro-v1.0.onnx", VOICE_DIR / "voices-v1.0.bin")
    for voice in ("am_fenrir", "am_puck", "am_onyx"):
        samples, rate = kokoro.create("OVERDRIVE!", voice=voice, speed=1.02, lang="en-us")
        sf.write(OUT_DIR / f"overdrive-{voice}.wav", normalize(samples), rate)


def render_knockout_bell() -> None:
    duration = 2.7
    t = np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE
    bell = np.zeros_like(t)
    rng = np.random.default_rng(1995)
    # Two hard rings. Inharmonic partials and slight frequency decay read as metal,
    # rather than the clean electronic chime used by the original placeholder.
    for strike in (0.0, 0.408):
        x = t - strike
        active = x >= 0
        y = x[active]
        hit = np.zeros_like(y)
        for ratio, gain, decay in (
            (1.00, 1.00, 2.4), (1.37, 0.72, 3.0), (1.91, 0.48, 3.8),
            (2.73, 0.28, 5.0), (4.08, 0.14, 7.0),
        ):
            phase = 2 * np.pi * (720 * ratio * y - 8 * ratio * y * y)
            hit += gain * np.sin(phase) * np.exp(-decay * y)
        hit += rng.normal(0, 0.26, len(y)) * np.exp(-35 * y)
        bell[active] += hit
    # Short, dark arcade-room reflections.
    dry = bell.copy()
    for delay, gain in ((0.071, 0.22), (0.109, 0.16), (0.173, 0.10), (0.257, 0.07)):
        offset = int(delay * SAMPLE_RATE)
        bell[offset:] += dry[:-offset] * gain
    fade = min(int(0.08 * SAMPLE_RATE), len(bell))
    bell[-fade:] *= np.linspace(1, 0, fade)
    sf.write(OUT_DIR / "knockout-bell.wav", normalize(bell, 0.88), SAMPLE_RATE)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_voices()
    render_knockout_bell()
    print(f"Rendered audio to {OUT_DIR}")
