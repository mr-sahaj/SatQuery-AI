"""Transparent, training-free baselines for Phase 2 satellite-image analysis.

These routines are deliberately labelled as visual heuristics. They are useful
for demos and for creating labels/QA views, but must be replaced or validated
with sensor-aware trained models before scientific or operational use.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class ChangeResult:
    changed_pixel_percent: float
    mean_visual_difference: float
    heatmap: Image.Image
    scope_note: str

    def summary(self) -> dict[str, Any]:
        return {
            "changed_pixel_percent": self.changed_pixel_percent,
            "mean_visual_difference_0_255": self.mean_visual_difference,
            "method": "RGB absolute-difference baseline after resize; no co-registration",
            "scope_note": self.scope_note,
        }


def compare_images(before: Image.Image, after: Image.Image, threshold: int = 35) -> ChangeResult:
    """Create an explainable RGB difference baseline and heatmap preview."""
    target = (min(before.width, after.width, 1024), min(before.height, after.height, 1024))
    before_array = np.asarray(before.convert("RGB").resize(target), dtype=np.int16)
    after_array = np.asarray(after.convert("RGB").resize(target), dtype=np.int16)
    difference = np.abs(after_array - before_array).mean(axis=2)
    changed = difference >= threshold
    intensity = np.clip((difference / 255.0) * 255.0, 0, 255).astype(np.uint8)
    heat = np.zeros((*intensity.shape, 3), dtype=np.uint8)
    heat[..., 0] = intensity
    heat[..., 1] = (intensity * 0.42).astype(np.uint8)
    heat[..., 2] = (255 - intensity) // 5
    heat[~changed] = np.array([5, 19, 34], dtype=np.uint8)
    return ChangeResult(
        changed_pixel_percent=round(float(changed.mean() * 100), 2),
        mean_visual_difference=round(float(difference.mean()), 2),
        heatmap=Image.fromarray(heat).filter(ImageFilter.GaussianBlur(radius=0.6)),
        scope_note="Images are resized but not geospatially co-registered; this is a visual-change baseline, not validated change detection.",
    )


def visual_feature_scout(image: Image.Image) -> dict[str, Any]:
    """Estimate broad RGB-visible classes for a transparent demo baseline."""
    array = np.asarray(image.convert("RGB").resize((512, 512)), dtype=np.int16)
    red, green, blue = array[..., 0], array[..., 1], array[..., 2]
    water = (blue > red * 1.08) & (blue > green * 1.03) & (blue > 60)
    vegetation = (green > red * 1.12) & (green > blue * 1.05) & (green > 55)
    bright_surface = (red > 155) & (green > 155) & (blue > 155)
    return {
        "water_like_visible_area_percent": round(float(water.mean() * 100), 2),
        "vegetation_like_visible_area_percent": round(float(vegetation.mean() * 100), 2),
        "bright_surface_like_visible_area_percent": round(float(bright_surface.mean() * 100), 2),
        "method": "RGB colour heuristic; not semantic segmentation or a physical area measurement.",
        "measurement_requirement": "For hectares/km², ingest a georeferenced raster and use its pixel resolution/CRS.",
    }


def preliminary_risk_flags(image: Image.Image) -> dict[str, Any]:
    """Return data-availability flags rather than pretending to predict disasters."""
    features = visual_feature_scout(image)
    return {
        "risk_output": "Not calculated from a single RGB image",
        "required_for_flood_risk": ["co-registered change images", "terrain/DEM", "rainfall", "exposure layers"],
        "required_for_fire_risk": ["thermal band or FIRMS/VIIRS hotspot evidence", "weather", "vegetation condition"],
        "visible_scene_summary": {key: features[key] for key in features if key.endswith("percent")},
        "scope_note": "A production risk index needs calibrated data, validation, and uncertainty reporting; it is not a disaster-probability predictor.",
    }
