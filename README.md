# SatQuery — Satellite Image Question Answering MVP

SatQuery is a hackathon-ready AI demo for asking natural-language questions about a satellite or aerial image. Upload an image, type a question, and receive a VLM answer alongside routing, confidence, image facts, and an evidence panel.

> **MVP scope:** This project demonstrates image upload, visual question answering, lightweight task routing, metadata extraction, image-derived evidence, and a polished Gradio UI. It does **not** claim to implement validated remote-sensing analytics, bi-temporal change detection, Optical+SAR fusion, geospatial grounding, or operational decision support. Those are planned future capabilities.

## Features

- VLM-based visual question answering (local Hugging Face model by default)
- Optional Hugging Face hosted-inference mode for lighter local hardware
- Lightweight query router: count, change, land-cover, infrastructure, yes/no, or general visual QA
- Evidence pane with image dimensions, format, EXIF/GPS when present, colour/brightness statistics, route, and model confidence
- Clean, dark Gradio demo UI with example questions
- Clear errors when models, tokens, or network access are unavailable

## Quick start

Requires **Python 3.10–3.12**. Python 3.11 is recommended.

```bash
git clone <your-github-repository-url>
cd SatQuery
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
pip install -r requirements.txt
python app.py
```

Open the local address shown in the terminal (normally `http://127.0.0.1:7860`). On its first local run, Transformers downloads the selected model.

## Model setup

The default model is `Salesforce/blip-vqa-base`. It is a general-purpose VQA model, **not a satellite-specialist model**—use this fact openly in the presentation. It is a pragmatic MVP baseline and runs on CPU, though a GPU is strongly preferred for a smooth demo.

### Local inference (default)

No token is required for public models. The first run needs internet access to download model weights, then Hugging Face caching allows later offline runs.

```bash
# optional: select another compatible Hugging Face VQA model
$env:SATQUERY_MODEL_ID = "Salesforce/blip-vqa-base"  # PowerShell
python app.py
```

### Hosted inference (optional)

Use this when the demo laptop is underpowered. Create a Hugging Face access token, then set it in your shell. Hosted availability and account limits depend on the provider.

```bash
$env:HF_TOKEN = "hf_your_token"
$env:SATQUERY_INFERENCE_MODE = "api"
python app.py
```

You can still select **Local Hugging Face** in the UI. Never commit your token.

## CPU, GPU, and demo preparation

- **CPU:** works, but first model load and each answer can take noticeable time. Use an 8 GB+ RAM machine and run once before judging.
- **NVIDIA GPU:** install the PyTorch build matching your CUDA version *before* `requirements.txt`; the app automatically uses CUDA when available.
- **Reliable demo:** download the model before the event, bring several tested JPG/PNG aerial or satellite images, and keep one short question ready (for example, “Is there a river visible?”).
- General VQA models can hallucinate or miss small objects. Treat answers as a demonstration, not a verified geospatial result.

## Project layout

```text
SatQuery/
├── app.py                     # Gradio entry point
├── requirements.txt
├── src/satquery/
│   ├── config.py               # Environment-backed configuration
│   ├── evidence.py             # Safe image/EXIF/statistics extraction
│   ├── routing.py              # Transparent lightweight router
│   ├── inference.py            # Local and hosted VLM adapters
│   └── service.py              # Orchestration and result schema
├── docs/ARCHITECTURE.md
├── docs/DEMO_SCRIPT.md
└── samples/README.md
```

## Troubleshooting

| Problem | What to do |
|---|---|
| `ModuleNotFoundError` | Confirm the virtual environment is active, then rerun `pip install -r requirements.txt`. |
| First run is slow/fails | Check internet access and Hugging Face availability; pre-download the model before the demo. |
| Out of memory / very slow CPU | Close other apps, use hosted inference, or test with a smaller image (the app resizes for inference). |
| `HF_TOKEN` error | Set a valid token only for API mode, restart the terminal, and do not place it in source files. |
| VLM answer looks wrong | Ask a simple, image-visible question; show confidence and limitations honestly. |
| PowerShell blocks activation | Run `Set-ExecutionPolicy -Scope Process Bypass` for that terminal, then activate again. |

## GitHub presentation checklist

```bash
git init
git add .
git commit -m "Build SatQuery MVP"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

Before pushing, verify that `.env`, tokens, model cache files, and large raw datasets are not tracked. Add a screenshot/GIF of the working UI to this README for a stronger presentation.

## Roadmap (not implemented in this MVP)

1. Bi-temporal, co-registered change detection with validated thresholds.
2. Optical + SAR fusion and sensor-specific preprocessing.
3. Geospatial grounding, coordinate-aware evidence, and map overlays.
4. Remote-sensing fine-tuning and benchmark evaluation on labeled datasets.
5. Multi-agent orchestration, provenance storage, and human review workflows.

## License

MIT — see [LICENSE](LICENSE).
