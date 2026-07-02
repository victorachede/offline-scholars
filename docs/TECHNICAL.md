# Technical Architecture

## Overview

Naija Offline AI is a three-module Python application with a Gradio web UI. All inference runs on CPU using quantized models. No network calls after the initial model download.

## Module 1: Tiv Translator

**Model:** T5-small fine-tuned on English-Tiv pairs  
**Training data:** ~5,000 sentence pairs scraped from Bible verses (bible.com `og:description` meta tags), community text, and educational materials  
**Training approach:** Sequence-to-sequence with task prefixes (`"translate English to Tiv: "` / `"translate Tiv to English: "`)  
**Metric:** BLEU 21.4 on verse-level test set  
**Inference:** HuggingFace `transformers`, beam search (n=4), CPU float32  
**Latency:** ~0.3s per sentence on i5-10th gen  

### Why T5-small

T5-small (60M parameters) fits comfortably within the 8GB RAM constraint. Larger models (T5-base, T5-large) showed marginal BLEU improvement (~+2) but 3-4x inference time. For low-resource translation at this scale, T5-small is the right tradeoff.

### The Tiv language challenge

Tiv is a Benue-Congo language with ~4M speakers. Before this project, it had:
- No entry in HuggingFace datasets
- No Google Translate support
- No neural translation models published anywhere

Key linguistic features that affected training:
- Tonal language (3 tones) — tones not marked in scraped text
- Verb-final word order in some constructions
- Noun class system different from European languages

BLEU 21 is a meaningful baseline for a language with this little data. Further improvements require a larger corpus.

## Module 2: JAMB Study Assistant

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

## Module 3: Voice Transcriber

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
| Tiv model (T5-small, float32) | ~250MB |
| Phi-3-mini (INT4 via Ollama) | ~3.5GB |
| Whisper tiny (INT8) | ~150MB |
| Python + Gradio | ~400MB |
| **Total** | **~4.3GB** |

Well within the 8GB constraint. Models are lazy-loaded — only the active tab's model is loaded unless all three are used.
