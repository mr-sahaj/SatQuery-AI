# SatQuery MVP architecture

```text
Uploaded image + user question
            │
            ├── Image preparation (RGB conversion, safe resize)
            ├── Evidence extractor (dimensions, EXIF, simple RGB statistics)
            └── Transparent rule router
                         │
                         ▼
              VLM adapter ───── Local Transformers
                         └───── Hosted Hugging Face API (optional)
                                      │
                                      ▼
                         Answer + confidence + scope notes
                                      │
                                      ▼
                                  Gradio UI
```

The router is deliberately lightweight and explainable. It does not replace the model and does not make scientific claims; it tags the likely request type and adds appropriate scope notes. The evidence extractor only reports facts available from the upload and basic pixel statistics. It does not infer coordinates, sensor calibration, or land-cover truth.

## Extension path

For a full research project, add data ingestion for GeoTIFF and STAC, sensor-specific preprocessing, co-registration, a tested change-detection model, remote-sensing VQA fine-tuning, benchmark datasets, and audit/provenance storage. Each capability should carry evaluation metrics and honest constraints.
