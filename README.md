# Offline Scholars

> A fully offline AI tutor for Nigerian students preparing for JAMB, WAEC, and NECO.
> Built for the **Africa Deep Tech Challenge 2026**.

---

## The problem

Millions of Nigerian students prepare for JAMB every year in areas with no reliable internet. Private tutors cost money most families don't have. Past question books go out of date. And when a student gets a question wrong, nobody explains *why*.

Offline Scholars fixes this. It runs entirely on a standard laptop — no internet, no API fees, no subscription. Open it, study, pass.

---

## How it works

Three modes, one install:

### 1. Practice Mode
The AI presents real JAMB/WAEC/NECO past questions one at a time. Student answers. AI marks it and explains the answer in plain conversational language — not just "correct answer is B" but *why* B is correct, what concept it tests, and what JAMB typically asks about it.

### 2. Ask Anything
Student types any question — "I don't understand equilibrium" or "explain the difference between speed and velocity" — and the local AI explains it from scratch. Like having a private tutor available 24/7 with no data required.

### 3. Mock CBT Exam
Timed, same format as the real JAMB CBT. 40 questions, subjects mixed, countdown timer. Submits and shows full score breakdown — every wrong answer explained.

---

## Hardware requirements

Designed for the contest constraints — and for the average Nigerian student's laptop:

- **RAM:** 8GB (runs in ~4-5GB)
- **GPU:** Not required — CPU only
- **Storage:** ~2.3GB for models
- **OS:** Windows 10+, macOS 12+, Ubuntu 20.04+

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/victorachede/offline-scholars
cd offline-scholars

# 2. Install Ollama (one time)
# Download from https://ollama.com and install

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Download models (one time, ~2.3GB, needs internet)
python scripts/download_models.py

# 5. Launch — now fully offline
python app.py
```

Opens at `http://localhost:7860`. Turn off your wifi. It still works.

---

## Stack

| Component | Technology | Size |
|---|---|---|
| AI tutor (explain + Q&A) | Phi-3-mini INT4 via Ollama | ~2.2GB |
| Speech to text | Whisper tiny (faster-whisper, INT8) | ~39MB |
| UI | Gradio (local server, share=False) | — |

---

## Subjects covered

Physics · Mathematics · English · Chemistry · Biology · Government · Economics · Literature

500+ past questions from JAMB (2015–2023), WAEC (2015–2023), NECO (2018–2022).

---

## Benchmarks

Tested on: Intel Core i5-10th gen, 8GB RAM, no GPU (Ubuntu 22.04)

| Task | Latency |
|---|---|
| AI explanation (short) | ~4s |
| Mock exam generation | ~1s |
| Voice transcription (5s audio) | ~1.8s |
| Peak RAM usage | ~4.3GB |

Full results: [docs/BENCHMARKS.md](docs/BENCHMARKS.md)

---

## Challenge criteria

| Criteria | How we meet it |
|---|---|
| **Fully offline** | Zero network calls after setup. Works with wifi off. |
| **8GB RAM, no GPU** | CPU-only inference. Peak usage ~4.3GB. |
| **Accuracy** | Phi-3-mini ~78% on JAMB MCQ. Explanations verified against curriculum. |
| **Speed** | ~4s per AI response on mid-range hardware. |
| **Open source** | MIT licensed. All code included. |
| **Real impact** | Solves a problem for millions of Nigerian students right now. |

---

## Why this matters

Nigeria has over 1.8 million JAMB candidates every year. Most are in states with poor internet. A private tutor costs ₦5,000–₦20,000 per month — unaffordable for most families.

Offline Scholars costs nothing after setup. It works in a village with no data. It explains concepts a textbook never could. And it never runs out of practice questions.

---

## Roadmap

- [x] Phi-3-mini offline Q&A engine
- [x] JAMB/WAEC/NECO past questions dataset (500+)
- [x] Mock CBT simulator
- [x] Voice input via Whisper tiny
- [ ] Fine-tune Phi-3 on Nigerian curriculum (in progress)
- [ ] Offline installer (.exe / .dmg)
- [ ] Android APK (post-challenge)

---

## About

Built and maintained by **Victor Achede**.

---

## License

MIT — use it, fork it, build on it.

---

*Submitted for the Africa Deep Tech Challenge 2026 · Deadline: August 25, 2026*


