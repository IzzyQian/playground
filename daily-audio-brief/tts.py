"""Turn a morning-update script into an MP3 with the offline Kokoro voice model.

Usage: python3 tts.py <script.txt> <out.mp3>

Needs: pip install kokoro-onnx soundfile, ffmpeg, and the model files in
$KOKORO_DIR (default /tmp/kokoro), downloadable from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
(kokoro-v1.0.int8.onnx and voices-v1.0.bin).
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

VOICE = os.environ.get("KOKORO_VOICE", "af_heart")
SPEED = float(os.environ.get("KOKORO_SPEED", "1.05"))


def main(script_path: str, out_path: str) -> None:
    model_dir = os.environ.get("KOKORO_DIR", "/tmp/kokoro")
    kokoro = Kokoro(
        os.path.join(model_dir, "kokoro-v1.0.int8.onnx"),
        os.path.join(model_dir, "voices-v1.0.bin"),
    )
    paragraphs = [p.strip() for p in open(script_path).read().split("\n\n") if p.strip()]
    chunks, rate = [], 24000
    for p in paragraphs:
        audio, rate = kokoro.create(p, voice=VOICE, speed=SPEED, lang="en-us")
        chunks.append(audio)
        chunks.append(np.zeros(int(rate * 0.45), dtype=audio.dtype))  # pause between paragraphs
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, np.concatenate(chunks), rate)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-codec:a", "libmp3lame", "-b:a", "96k", out_path],
        check=True,
    )
    os.unlink(tmp.name)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
