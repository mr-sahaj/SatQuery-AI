# SatQuery Phase 2 — data and training plan

## What is implemented now

- An RGB visual-difference baseline for two uploaded images.
- Broad, visibly water-/vegetation-/bright-surface-like pixel summaries.
- Explicit data requirements for future flood and fire risk indicators.

These are **not trained remote-sensing models** and must not be presented as validated detections or measurements.

## Training tracks

### 1. Change detection

- **Inputs:** co-registered before/after optical or SAR image pairs; cloud masks; change labels.
- **Output:** binary or multi-class change mask (for example: water expansion, vegetation loss, built-up growth).
- **Evaluation:** IoU/F1 per class, precision/recall, and tests on geographically held-out regions.
- **Minimum data structure:** `data/change/{train,val,test}/{before,after,label}` with identical filenames per triplet.

### 2. Feature segmentation and size analysis

- **Inputs:** georeferenced multi-band scenes plus polygon masks for water, buildings, roads, burn scars, and vegetation.
- **Output:** class mask, confidence, pixel count, and area using the raster's projected pixel resolution.
- **Evaluation:** per-class IoU and absolute area error against known polygons.
- **Important:** RGB uploads alone do not support reliable hectare/km² measurements. Preserve GeoTIFF CRS and affine transform.

### 3. Fire and thermal intelligence

- **Inputs:** Landsat Level-2 surface-temperature product or thermal bands, plus time/location-matched NASA FIRMS hotspot records.
- **Output:** thermal anomaly evidence, hotspot overlay, source/sensor/time, and uncertainty—not reconstructed thermal data from RGB.
- **Evaluation:** match rate against independent hotspot labels; spatial and time-tolerance reporting.

### 4. Disaster risk index

- **Inputs:** hazard signals, terrain, weather/rainfall, land cover, and exposure/vulnerability layers.
- **Output:** a calibrated risk category with contributing factors and uncertainty.
- **Guardrail:** never claim it predicts whether a disaster will occur. It is decision support and requires local validation.

## Training environment

Use a GPU notebook/workstation after the data contract is fixed. Record dataset version, geographic split, model checkpoint, metrics, and failures. Start with pretrained segmentation/change-detection backbones, fine-tune only after the label quality and baselines are established.
