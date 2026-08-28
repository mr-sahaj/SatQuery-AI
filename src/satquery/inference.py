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
def _local_model(model_id: str):
    """Load BLIP directly instead of the removed Transformers VQA pipeline."""
    import torch
    from transformers import BlipForQuestionAnswering, BlipProcessor

    processor = BlipProcessor.from_pretrained(model_id)
    model = BlipForQuestionAnswering.from_pretrained(model_id)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return processor, model, device


def ask_local(image: Image.Image, question: str, settings: Settings) -> InferenceResult:
    try:
        processor, model, device = _local_model(settings.model_id)
        inputs = processor(images=image, text=question, return_tensors="pt")
        inputs = {name: value.to(device) for name, value in inputs.items()}
        output = model.generate(**inputs, max_new_tokens=30)
        answer = processor.decode(output[0], skip_special_tokens=True).strip()
        return InferenceResult(answer or "No answer returned", None, f"Local BLIP: {settings.model_id} ({device})")
    except Exception as exc:  # surfaced cleanly in the UI
        raise RuntimeError(f"Local model could not answer. Check the model download, memory, model compatibility, and internet connection. Details: {exc}") from exc


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
