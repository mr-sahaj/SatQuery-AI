from __future__ import annotations

from typing import Any

from PIL import ExifTags, Image, ImageStat


def prepare_image(image: Image.Image, max_side: int) -> Image.Image:
    result = image.convert("RGB")
    result.thumbnail((max_side, max_side))
    return result


def extract_evidence(image: Image.Image) -> dict[str, Any]:
    rgb = image.convert("RGB")
    stat = ImageStat.Stat(rgb)
    metadata: dict[str, Any] = {
        "image_size_px": f"{image.width} × {image.height}",
        "format": image.format or "unknown (uploaded image)",
        "color_mode": image.mode,
        "mean_rgb": [round(value, 1) for value in stat.mean[:3]],
        "brightness_mean_0_255": round(sum(stat.mean[:3]) / 3, 1),
    }
    try:
        exif = image.getexif()
        if exif:
            named = {ExifTags.TAGS.get(k, str(k)): str(v)[:180] for k, v in exif.items()}
            metadata["exif_fields"] = named
        else:
            metadata["exif_fields"] = "No EXIF metadata found"
    except (AttributeError, ValueError, OSError):
        metadata["exif_fields"] = "EXIF unavailable"
    return metadata
