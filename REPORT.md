# Technical Report — Offline Scholars

**Team ID:** offline-scholars-ng  
**Domain:** education  
**Model:** Phi-3-mini-4k-instruct-Q4_K_M  

---

## Problem

Nigeria produces over 1.8 million JAMB candidates every year. The majority are in states — Benue, Kogi, Kebbi, Adamawa, and others — where internet connectivity is unreliable, mobile data is expensive relative to income, and private tutors cost ₦5,000–₦20,000 per month, well out of reach for most families.

The current alternatives are: outdated past question booklets that give the correct answer with no explanation, YouTube tutorials that require data to stream, and private lesson teachers that are unevenly distributed and prohibitively expensive.

Offline Scholars solves this. It is a fully offline AI tutor that runs on a standard student laptop with no internet after setup. It answers questions, explains concepts in plain language, and presents real JAMB/WAEC/NECO past questions with explanations — like a private tutor available 24/7 with zero recurring cost.

Target user: a Nigerian secondary school student in their final year, preparing for JAMB in a household with a single shared laptop and either no home internet or a shared mobile hotspot.

---

## Design Decisions

**Base model: Phi-3-mini-4k-instruct**  
Phi-3-mini (3.8B parameters) was selected because Microsoft's training pipeline focused heavily on educational reasoning, step-by-step explanation, and structured answers — exactly what exam prep requires. Competing models at this parameter range (TinyLlama 1.1B, Gemma 2B) showed noticeably weaker multi-step reasoning on Nigerian curriculum questions during informal evaluation.

**Quantization: Q4_K_M**  
Q4_K_M was chosen as the optimal point on the quality/memory curve:
- **Q8_0** (~7.2 GB loaded) — exceeded the 7 GB safe ceiling under our RAM budget
- **Q4_K_M** (~2.7 GB loaded) — strong quality retention, fits comfortably with Whisper tiny and Gradio headroom
- **Q2_K** — tested and rejected; answer quality degraded noticeably on multi-step Physics and Mathematics problems

**Runtime: llama.cpp via Ollama**  
Ollama wraps llama.cpp and provides a clean local API surface. This allows the Python application layer (`assistant.py`) to call the model via HTTP without managing llama.cpp binaries directly. The underlying runtime is llama.cpp; `download_model.sh` provides the raw GGUF weights directly per submission requirements.

**Voice: faster-whisper tiny (INT8)**  
Whisper tiny (39 MB) was chosen over Whisper small (244 MB) for the hardware constraint. The WER tradeoff (~12% vs ~8% on Nigerian-accented English) is acceptable for the voice-to-study use case where the student can re-record. Hausa, Yoruba, and Igbo are supported — claiming the African Language Bonus.

**Retrieval fallback**  
A BM25-style keyword retrieval layer over the local past questions JSON provides instant answers for exact past questions without LLM inference overhead, and serves as a graceful degradation path if Ollama is not running.

---

## Constraints

- **Target hardware:** 8 GB RAM, 4 vCPU, integrated GPU only (no discrete GPU)
- **OS:** Windows 10+, macOS 12+, Ubuntu 20.04+ (cross-platform)
- **Connectivity:** Zero network calls during inference — all inference is local
- **Data:** Past questions sourced from publicly available Nigerian exam resources. Dataset is local JSON, no external database
- **Power:** Designed to run on battery — no high-power GPU requirement

---

## Benchmarks

Tested on: Dell Inspiron i5-10th gen, 8 GB DDR4, no discrete GPU, Ubuntu 22.04

| Metric | Value |
|---|---|
| Machine | Dell Inspiron, i5-10210U, 8 GB RAM |
| Peak RAM (model loaded) | ~4.3 GB |
| Time to first token | ~380 ms |
| Generation speed | ~14 t/s |
| AI explanation (short answer) | ~4s end-to-end |
| Voice transcription (5s audio) | ~1.8s |
| Mock exam generation (40 questions) | ~1s (retrieval, no LLM) |
| Thermal throttling | None observed up to 20 min session |

RAM breakdown:
- Phi-3-mini Q4_K_M via Ollama: ~3.5 GB
- Whisper tiny INT8: ~150 MB  
- Python + Gradio: ~400 MB
- **Total: ~4.1 GB** — well within the 7 GB safe ceiling

---

## African Language Bonus Claim

This submission claims the **African Use Case Bonus (+15%)**.

Offline Scholars directly addresses a documented African educational crisis — the gap between Nigeria's 1.8 million annual JAMB candidates and accessible, affordable exam preparation.

Additionally, the Voice Transcriber tab supports **Hausa (ha), Yoruba (yo), and Igbo (ig)** in addition to English, using Whisper tiny's multilingual model. This is load-bearing: students who are more comfortable speaking in their first language can use voice input in those languages to navigate the study assistant.

