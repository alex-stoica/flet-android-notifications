"""Generate a simple notification beep WAV file using only stdlib."""

import math
import struct
import wave
from pathlib import Path

OUTPUT = Path(__file__).parent / "test_resources" / "test_beep.wav"

SAMPLE_RATE = 44100
DURATION = 0.3  # seconds
FREQUENCY = 880  # Hz (A5 — distinct from default notification sounds)
AMPLITUDE = 0.6
FADE_MS = 10  # fade in/out to avoid clicks


def generate():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    n_samples = int(SAMPLE_RATE * DURATION)
    fade_samples = int(SAMPLE_RATE * FADE_MS / 1000)

    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        value = AMPLITUDE * math.sin(2 * math.pi * FREQUENCY * t)

        # fade envelope
        if i < fade_samples:
            value *= i / fade_samples
        elif i > n_samples - fade_samples:
            value *= (n_samples - i) / fade_samples

        samples.append(int(value * 32767))

    with wave.open(str(OUTPUT), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    print(f"generated {OUTPUT} ({n_samples} samples, {DURATION}s, {FREQUENCY}Hz)")


if __name__ == "__main__":
    generate()
