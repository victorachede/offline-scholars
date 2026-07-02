"""
Tiv Translator — English ↔ Tiv neural machine translation.
Uses fine-tuned T5-small: victorachede/tiv-translator on HuggingFace.
Runs fully offline after first model download.
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import os

MODEL_ID = "victorachede/tiv-translator"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../models/tiv-translator")


class TivTranslator:
    def __init__(self, device: str = "cpu"):
        self.device = device
        self._model = None
        self._tokenizer = None

    def _load(self):
        if self._model is not None:
            return
        print("Loading Tiv translation model...")
        self._tokenizer = T5Tokenizer.from_pretrained(
            MODEL_ID,
            cache_dir=CACHE_DIR,
            local_files_only=False,  # set True after first download
        )
        self._model = T5ForConditionalGeneration.from_pretrained(
            MODEL_ID,
            cache_dir=CACHE_DIR,
            local_files_only=False,
            torch_dtype=torch.float32,
        ).to(self.device)
        self._model.eval()
        print("Model loaded.")

    def translate(self, text: str, direction: str = "en→tiv") -> str:
        """
        Translate text between English and Tiv.

        Args:
            text: Input text to translate
            direction: "en→tiv" or "tiv→en"

        Returns:
            Translated string
        """
        self._load()

        prefix = "translate English to Tiv: " if direction == "en→tiv" else "translate Tiv to English: "
        input_text = prefix + text.strip()

        inputs = self._tokenizer(
            input_text,
            return_tensors="pt",
            max_length=256,
            truncation=True,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_length=256,
                num_beams=4,
                early_stopping=True,
            )

        return self._tokenizer.decode(outputs[0], skip_special_tokens=True)

    def batch_translate(self, texts: list[str], direction: str = "en→tiv") -> list[str]:
        """Translate a list of texts in one pass."""
        return [self.translate(t, direction) for t in texts]


if __name__ == "__main__":
    t = TivTranslator()
    print(t.translate("Good morning, how are you?", "en→tiv"))
    print(t.translate("A jôron u sha?", "tiv→en"))
