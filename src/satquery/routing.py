from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    name: str
    reason: str
    disclaimer: str | None = None


def route_question(question: str) -> Route:
    q = question.lower()
    if any(word in q for word in ("change", "before", "after", "compare", "difference")):
        return Route("change_detection_request", "Detected temporal/comparison wording.", "This MVP accepts one image and cannot perform bi-temporal change detection.")
    if any(word in q for word in ("sar", "radar", "optical fusion", "fusion")):
        return Route("sensor_fusion_request", "Detected SAR or fusion wording.", "Optical + SAR fusion is a future capability, not implemented in this MVP.")
    if any(word in q for word in ("how many", "count", "number of")):
        return Route("counting", "Detected counting language; passes query to the VLM.", "Counts are approximate VLM observations, not validated object detections.")
    if any(word in q for word in ("road", "building", "bridge", "airport", "dam", "infrastructure")):
        return Route("infrastructure", "Detected infrastructure vocabulary; passes query to the VLM.")
    if any(word in q for word in ("forest", "water", "river", "lake", "farm", "crop", "vegetation", "land cover")):
        return Route("land_cover", "Detected land-cover vocabulary; passes query to the VLM.")
    if q.startswith(("is ", "are ", "do ", "does ", "can ")):
        return Route("presence_check", "Detected a yes/no visual question; passes query to the VLM.")
    return Route("general_visual_qa", "No specialised rule matched; using general visual question answering.")
