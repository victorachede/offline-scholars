# Technical Architecture

## Overview

Offline Scholars is a two-module Python application with a Gradio web UI. All inference runs on CPU using quantized models. No network calls after the initial model download.

## Module 1: JAMB Study Assistant

**Primary model:** Phi-3-mini-4k-instruct (INT4 quantized via Ollama)  
**Model size:** ~2.2GB on disk  
**RAM usage:** ~3.5GB loaded  
**Fallback:** Keyword retrieval from local past questions JSON  

### Why Phi-3-mini

Phi-3-mini achieves near-GPT-3.5 quality on reasoning tasks at 3.8B parameters. With INT4 quantization via Ollama:
- Runs on CPU in ~4-5s per response
- Fits within 8GB RAM alongside the other models
- Microsoft's training focused heavily on educational content — good fit for exam prep

### Retrieval fallback

If Ollama is not running, the assistant falls back to BM25-style keyword retrieval over the local past questions JSON. This gives instant answers for exact past questions without any LLM overhead.

### Past questions dataset

500+ questions scraped from public Nigerian exam resources:
- Subjects: Physics, Math, English, Chemistry, Biology, Government, Economics, Literature
- Exams: JAMB (2015-2023), WAEC (2015-2023), NECO (2018-2022)
- Format: `{id, subject, year, exam, question, options, answer, explanation}`

## Module 2: Voice Transcriber

**Model:** Whisper tiny (39MB)  
**Backend:** `faster-whisper` with INT8 quantization on CPU  
**Languages:** English (en), Hausa (ha), Yoruba (yo), Igbo (ig)  
**Latency:** ~1.8s for 5s audio on CPU  

### Whisper tiny vs small

Whisper tiny (39MB) vs small (244MB): tiny achieves WER ~12% on Nigerian-accented English vs ~8% for small. The 5x size difference favors tiny for the hardware constraint. Hausa/Yoruba/Igbo accuracy is lower (~20-25% WER) due to limited training data in the base Whisper model — but still useful for keyword extraction and note-taking.

## UI: Gradio

Gradio launches a local web server at `127.0.0.1:7860`. `share=False` ensures no traffic goes to Gradio's cloud infrastructure — fully offline.

## RAM budget

| Component | Peak RAM |
|---|---|
| Phi-3-mini (INT4 via Ollama) | ~3.5GB |
| Whisper tiny (INT8) | ~150MB |
| Python + Gradio | ~400MB |
| **Total** | **~4.1GB** |

Well within the 8GB constraint. Models are lazy-loaded — only the active tab's model is loaded on first use.
