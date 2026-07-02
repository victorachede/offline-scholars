"""
Download all models for offline use.
Run once before launching the app: python scripts/download_models.py
Total download: ~2.5GB
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MODELS_DIR = ROOT / "models"

def download_tiv_model():
    print("\n[1/3] Downloading Tiv translation model (~240MB)...")
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    cache = str(MODELS_DIR / "tiv-translator")
    os.makedirs(cache, exist_ok=True)
    T5Tokenizer.from_pretrained("victorachede/tiv-translator", cache_dir=cache)
    T5ForConditionalGeneration.from_pretrained("victorachede/tiv-translator", cache_dir=cache)
    print("✓ Tiv model downloaded.")


def download_whisper():
    print("\n[2/3] Downloading Whisper tiny (~39MB)...")
    from faster_whisper import WhisperModel
    cache = str(MODELS_DIR / "whisper")
    os.makedirs(cache, exist_ok=True)
    WhisperModel("tiny", device="cpu", compute_type="int8", download_root=cache)
    print("✓ Whisper downloaded.")


def download_phi3():
    print("\n[3/3] Pulling Phi-3 mini via Ollama (~2.2GB)...")
    print("   Make sure Ollama is installed: https://ollama.com")
    import subprocess
    result = subprocess.run(["ollama", "pull", "phi3:mini"], capture_output=False)
    if result.returncode == 0:
        print("✓ Phi-3 mini downloaded.")
    else:
        print("⚠ Ollama pull failed. Install Ollama and run: ollama pull phi3:mini")
        print("  The study assistant will fall back to retrieval-only mode without it.")


if __name__ == "__main__":
    print("=" * 50)
    print("Offline Scholars — Model Setup")
    print("=" * 50)

    MODELS_DIR.mkdir(exist_ok=True)

    try:
        download_tiv_model()
    except Exception as e:
        print(f"✗ Tiv model failed: {e}")

    try:
        download_whisper()
    except Exception as e:
        print(f"✗ Whisper failed: {e}")

    try:
        download_phi3()
    except Exception as e:
        print(f"✗ Phi-3 failed: {e}")

    print("\n" + "=" * 50)
    print("Setup complete. Run: python app.py")
    print("=" * 50)
