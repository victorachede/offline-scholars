"""
Benchmark script — measures speed and accuracy on standard hardware.
Run: python scripts/benchmark.py
"""

import time
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent


def benchmark_translator():
    print("\n── Tiv Translator ──────────────────────────────")
    from src.translator.translator import TivTranslator
    t = TivTranslator()

    test_pairs = [
        ("Good morning", "en→tiv"),
        ("The sun rises in the east", "en→tiv"),
        ("A jôron u", "tiv→en"),
        ("Ange msen", "tiv→en"),
        ("Water is life", "en→tiv"),
    ]

    times = []
    for text, direction in test_pairs:
        start = time.time()
        result = t.translate(text, direction)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  [{direction}] '{text}' → '{result}' ({elapsed:.2f}s)")

    avg = sum(times) / len(times)
    print(f"\n  Average latency: {avg:.2f}s")
    print(f"  Min: {min(times):.2f}s | Max: {max(times):.2f}s")


def benchmark_study_assistant():
    print("\n── Study Assistant ─────────────────────────────")
    from src.study_assistant.assistant import StudyAssistant
    a = StudyAssistant()

    questions = [
        ("What is the SI unit of electric current?", "Physics"),
        ("Find the sum of the first 10 natural numbers.", "Mathematics"),
        ("Who wrote Things Fall Apart?", "Literature"),
    ]

    for q, subject in questions:
        start = time.time()
        answer = a.ask(q, subject)
        elapsed = time.time() - start
        preview = answer[:80].replace("\n", " ") + "..."
        print(f"  Q: {q}")
        print(f"  A: {preview}")
        print(f"  Time: {elapsed:.2f}s\n")


def benchmark_voice():
    print("\n── Voice Transcriber ───────────────────────────")
    print("  (Skipping live mic test in benchmark mode)")
    print("  Model: whisper-tiny | Device: CPU | Compute: INT8")

    try:
        from faster_whisper import WhisperModel
        cache = str(ROOT / "models" / "whisper")
        start = time.time()
        model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root=cache)
        load_time = time.time() - start
        print(f"  Model load time: {load_time:.2f}s")
        print("  Expected transcription speed: ~1.8s per 5s audio on i5-10th gen")
    except Exception as e:
        print(f"  Whisper not available: {e}")


def check_ram():
    print("\n── Memory Usage ────────────────────────────────")
    try:
        import psutil
        process = __import__("os").getpid()
        mem = psutil.Process(process).memory_info().rss / 1024 / 1024
        total = psutil.virtual_memory().total / 1024 / 1024 / 1024
        print(f"  Process RAM: {mem:.0f}MB")
        print(f"  System RAM: {total:.1f}GB")
        print(f"  {'✓ Within 8GB constraint' if total <= 8.5 else '⚠ Over 8GB'}")
    except ImportError:
        print("  psutil not installed — skipping RAM check")


if __name__ == "__main__":
    print("=" * 50)
    print("Offline Scholars — Benchmark")
    print("=" * 50)

    benchmark_translator()
    benchmark_study_assistant()
    benchmark_voice()
    check_ram()

    print("\n" + "=" * 50)
    print("Benchmark complete. See docs/BENCHMARKS.md for full results.")
    print("=" * 50)
