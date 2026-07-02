"""
Offline Scholars — main application entry point.
Launches a Gradio UI with two tabs: Study Assistant, Voice.
Runs fully offline at http://localhost:7860
"""

import gradio as gr
from src.study_assistant.assistant import StudyAssistant
from src.voice.transcriber import VoiceTranscriber

# Lazy-load models so startup is fast
assistant = StudyAssistant()
transcriber = VoiceTranscriber()

SUBJECTS = ["Physics", "Mathematics", "English", "Chemistry", "Biology", "Government", "Economics", "Literature"]


# ── Study Assistant UI ───────────────────────────────────────────────────────
def ask_question(question: str, subject: str) -> str:
    if not question.strip():
        return "Please type a question."
    return assistant.ask(question, subject if subject != "All subjects" else None)


# ── Voice UI ─────────────────────────────────────────────────────────────────
def transcribe_audio(audio, language: str) -> str:
    if audio is None:
        return "No audio received."
    try:
        result = transcriber.transcribe_file(audio, language)
        return result["text"]
    except Exception as e:
        return f"Error: {str(e)}"


# ── Build UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="Offline Scholars",
    theme=gr.themes.Soft(primary_hue="green"),
    css="""
    .tab-nav button { font-weight: 600; }
    .output-text { font-size: 15px; line-height: 1.6; }
    footer { display: none !important; }
    """
) as app:

    gr.Markdown("""
    # 🇳🇬 Offline Scholars
    **Fully offline AI tutor for Nigerian exam prep.**
    JAMB · WAEC · NECO · No internet required · No API fees
    """)

    with gr.Tabs():

        # ── Tab 1: JAMB Study Assistant ──────────────────────────────────────
        with gr.Tab("JAMB Study Assistant"):
            gr.Markdown("### Offline JAMB/WAEC/NECO Tutor\nAsk any question about your subjects. Explains concepts, past exam questions, and common traps.")
            with gr.Row():
                study_subject = gr.Dropdown(
                    choices=["All subjects"] + SUBJECTS,
                    value="All subjects",
                    label="Subject (optional)",
                    scale=1,
                )
            study_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. What is the difference between speed and velocity?",
                lines=3,
            )
            study_btn = gr.Button("Ask", variant="primary")
            study_output = gr.Textbox(label="Answer", lines=10, interactive=False, elem_classes="output-text")

            study_btn.click(ask_question, inputs=[study_input, study_subject], outputs=study_output)
            study_input.submit(ask_question, inputs=[study_input, study_subject], outputs=study_output)

            gr.Examples(
                examples=[
                    ["What is the SI unit of electric current?", "Physics"],
                    ["Explain the law of demand with an example.", "Economics"],
                    ["What is the difference between mitosis and meiosis?", "Biology"],
                    ["Who wrote Things Fall Apart?", "Literature"],
                ],
                inputs=[study_input, study_subject],
            )

        # ── Tab 2: Voice Transcriber ─────────────────────────────────────────
        with gr.Tab("Voice Transcriber"):
            gr.Markdown("### Offline Speech to Text\nRecord your voice and get a transcript. Works for English, Hausa, Yoruba, and Igbo.")
            with gr.Row():
                voice_lang = gr.Dropdown(
                    choices=["English", "Hausa", "Yoruba", "Igbo"],
                    value="English",
                    label="Language",
                    scale=1,
                )
            voice_input = gr.Audio(
                label="Record or upload audio",
                type="filepath",
                sources=["microphone", "upload"],
            )
            voice_btn = gr.Button("Transcribe", variant="primary")
            voice_output = gr.Textbox(label="Transcript", lines=6, interactive=False, elem_classes="output-text")

            voice_btn.click(transcribe_audio, inputs=[voice_input, voice_lang], outputs=voice_output)

    gr.Markdown("""
    ---
    Built by **Victor** (Black Sheep Co) · [asktc.live](https://asktc.live)

    *Submitted for the Africa Deep Tech Challenge 2026*
    """)


if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,       # fully offline — no Gradio cloud share
        inbrowser=True,
    )
