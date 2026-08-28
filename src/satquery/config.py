from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    model_id: str
    hf_token: str | None
    default_mode: str
    host: str
    port: int
    max_image_side: int

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        return cls(
            model_id=os.getenv("SATQUERY_MODEL_ID", "Salesforce/blip-vqa-base"),
            hf_token=os.getenv("HF_TOKEN") or None,
            default_mode=os.getenv("SATQUERY_INFERENCE_MODE", "local").lower(),
            host=os.getenv("SATQUERY_HOST", "127.0.0.1"),
            port=int(os.getenv("SATQUERY_PORT", "7860")),
            max_image_side=int(os.getenv("SATQUERY_MAX_IMAGE_SIDE", "1024")),
        )
