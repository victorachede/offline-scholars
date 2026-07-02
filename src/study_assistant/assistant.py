"""
JAMB Study Assistant — offline Q&A for Nigerian exam prep.
Uses Phi-3-mini-4k quantized (INT4) via Ollama for local inference.
Falls back to retrieval-based answers from the past questions dataset.
"""

import json
import os
import re
from pathlib import Path

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "questions"
MODEL_NAME = "phi3:mini"

SYSTEM_PROMPT = """You are an expert Nigerian exam tutor helping students prepare for JAMB, WAEC, and NECO.
You explain concepts clearly, point out common exam traps, and always relate answers back to the Nigerian curriculum.
Keep answers concise but complete. If you reference a past exam question, say which year and exam it was from.
You run fully offline — never tell the user to "check online" or "visit a website"."""


class StudyAssistant:
    def __init__(self):
        self._questions = None
        self._load_questions()

    def _load_questions(self):
        """Load past questions from local JSON files."""
        self._questions = []
        if not DATA_PATH.exists():
            return
        for f in DATA_PATH.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    if isinstance(data, list):
                        self._questions.extend(data)
            except Exception:
                pass

    def _retrieve_relevant(self, query: str, k: int = 3) -> list[dict]:
        """Simple keyword retrieval from past questions."""
        query_lower = query.lower()
        scored = []
        for q in self._questions:
            text = f"{q.get('question', '')} {q.get('explanation', '')}".lower()
            score = sum(1 for word in query_lower.split() if word in text and len(word) > 3)
            if score > 0:
                scored.append((score, q))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [q for _, q in scored[:k]]

    def ask(self, question: str, subject: str | None = None) -> str:
        """
        Answer a study question offline.

        Args:
            question: The student's question
            subject: Optional subject hint (Physics, Mathematics, etc.)

        Returns:
            Answer string
        """
        # Try retrieval first
        relevant = self._retrieve_relevant(question)
        context = ""
        if relevant:
            context = "\n\nRelevant past questions for context:\n"
            for q in relevant:
                context += f"- {q.get('exam', '')} {q.get('year', '')}: {q.get('question', '')}\n"
                context += f"  Answer: {q.get('answer', '')}. {q.get('explanation', '')}\n"

        if OLLAMA_AVAILABLE:
            return self._ask_llm(question, context, subject)
        else:
            return self._ask_retrieval_only(question, relevant)

    def _ask_llm(self, question: str, context: str, subject: str | None) -> str:
        """Use local Phi-3 via Ollama."""
        subject_hint = f" (Subject: {subject})" if subject else ""
        user_msg = f"Student question{subject_hint}: {question}{context}"

        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                options={"num_predict": 512, "temperature": 0.3},
            )
            return response["message"]["content"]
        except Exception as e:
            return self._ask_retrieval_only(question, self._retrieve_relevant(question))

    def _ask_retrieval_only(self, question: str, relevant: list[dict]) -> str:
        """Fallback when Ollama isn't running — pure retrieval."""
        if not relevant:
            return "I couldn't find a direct match for that question. Try rephrasing or check that Ollama is running for full AI answers."

        best = relevant[0]
        answer = f"**{best.get('exam', '')} {best.get('year', '')}**\n\n"
        answer += f"Q: {best.get('question', '')}\n\n"
        answer += f"Answer: **{best.get('answer', '')}**\n\n"
        answer += f"Explanation: {best.get('explanation', '')}"
        return answer

    def generate_quiz(self, subject: str, count: int = 5) -> list[dict]:
        """Return random past questions for a subject."""
        import random
        pool = [q for q in self._questions if q.get("subject", "").lower() == subject.lower()]
        return random.sample(pool, min(count, len(pool)))

    def check_answer(self, question_id: str, selected: str) -> dict:
        """Check a student's MCQ answer."""
        q = next((x for x in self._questions if x.get("id") == question_id), None)
        if not q:
            return {"correct": False, "error": "Question not found"}
        correct = q.get("answer")
        return {
            "correct": selected == correct,
            "correct_answer": correct,
            "explanation": q.get("explanation", ""),
        }


if __name__ == "__main__":
    assistant = StudyAssistant()
    print(assistant.ask("What is the SI unit of electric current?", "Physics"))
