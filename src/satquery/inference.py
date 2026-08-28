from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from PIL import Image

from .config import Settings


@dataclass(frozen=True)
class InferenceResult:
    answer: str
    confidence: float | None
    backend: str


@lru_cache(maxsize=2)
def _local_pipeline(model_id: str):
    from transformers import pipeline
    return pipeline("visual-question-answering", model=model_id)


def ask_local(image: Image.Image, question: str, settings: Settings) -> InferenceResult:
    try:
        predictions = _local_pipeline(settings.model_id)(image=image, question=question, top_k=1)
        best = predictions[0] if isinstance(predictions, list) else predictions
        return InferenceResult(str(best.get("answer", "No answer returned")), _score(best.get("score")), f"Local: {settings.model_id}")
    except Exception as exc:  # surfaced cleanly in the UI
        raise RuntimeError(f"Local model could not answer. Check the model download, memory, and internet connection. Details: {exc}") from exc


def ask_api(image: Image.Image, question: str, settings: Settings) -> InferenceResult:
    if not settings.hf_token:
        raise RuntimeError("Hosted API mode requires HF_TOKEN. Add it to your shell or choose Local Hugging Face.")
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=settings.hf_token)
        predictions = client.visual_question_answering(image=image, question=question, model=settings.model_id)
        best = predictions[0] if isinstance(predictions, list) else predictions
        answer = _field(best, "answer", "No answer returned")
        return InferenceResult(str(answer), _score(_field(best, "score")), f"Hosted API: {settings.model_id}")
    except Exception as exc:
        raise RuntimeError(f"Hosted inference failed. Verify HF_TOKEN, account access, and network connection. Details: {exc}") from exc


def _score(value: object) -> float | None:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _field(value: object, key: str, default: object = None) -> object:
    """Read a field from either the SDK response object or a JSON dictionary."""
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)
