from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from PIL import Image

from .config import Settings
from .evidence import extract_evidence, prepare_image
from .inference import ask_api, ask_local
from .routing import Route, route_question


@dataclass
class QueryResult:
    answer: str
    route: Route
    inference_mode: str
    model: str
    confidence: float | None
    evidence: dict[str, Any]

    def to_summary(self) -> dict[str, Any]:
        return {
            "route": asdict(self.route),
            "inference_mode": self.inference_mode,
            "model": self.model,
            "confidence": self.confidence,
            "scope_note": "VLM output is indicative visual QA, not validated remote-sensing analysis.",
        }

    def evidence_markdown(self) -> str:
        lines = ["### Evidence & metadata", "", "**Image-derived facts**"]
        for key, value in self.evidence.items():
            lines.append(f"- `{key}`: {value}")
        lines += ["", "**Interpretation note**", "- The answer is a model prediction from pixels; it is not independent proof or a geospatial measurement."]
        if self.route.disclaimer:
            lines.append(f"- {self.route.disclaimer}")
        return "\n".join(lines)


class SatQueryService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def ask(self, image: Image.Image, question: str, ui_mode: str) -> QueryResult:
        route = route_question(question)
        prepared = prepare_image(image, self.settings.max_image_side)
        evidence = extract_evidence(image)
        if ui_mode == "Hosted Hugging Face API":
            result = ask_api(prepared, question, self.settings)
            mode = "hosted_api"
        else:
            result = ask_local(prepared, question, self.settings)
            mode = "local"
        return QueryResult(result.answer, route, mode, result.backend, result.confidence, evidence)
