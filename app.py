"""SatQuery research-console UI and Gradio entry point."""
from __future__ import annotations

from datetime import datetime

import gradio as gr
from PIL import Image

from src.satquery.analytics import compare_images, preliminary_risk_flags, visual_feature_scout
from src.satquery.config import Settings
from src.satquery.service import SatQueryService

settings = Settings.from_environment()
service = SatQueryService(settings)


def mode_note(workspace_mode: str) -> str:
    notes = {
        "Single Optical": "**Active MVP mode.** Upload one optical/aerial image and ask a visual question.",
        "Single SAR": "**Preview UI only.** SAR-specific preprocessing and inference are not implemented in this MVP.",
        "Optical + SAR": "**Future capability.** Cross-modal fusion is shown as a planned workflow, not an active analysis path.",
        "Bi-temporal": "**Future capability.** This MVP does not yet perform registered before/after change detection.",
    }
    return notes[workspace_mode]


def analyze(image: Image.Image | None, question: str, inference_mode: str, workspace_mode: str):
    if image is None:
        return "Upload a satellite or aerial image to begin.", {"status": "waiting_for_image", "workspace_mode": workspace_mode}, "### Evidence\nNo image uploaded yet.", "● READY — WAITING FOR SCENE"
    if not question or not question.strip():
        return "Enter a question about the image to begin analysis.", {"status": "waiting_for_question", "workspace_mode": workspace_mode}, "### Evidence\nImage loaded; no query submitted.", "● READY — WAITING FOR QUERY"
    try:
        result = service.ask(image, question.strip(), inference_mode)
        summary = result.to_summary()
        summary["workspace_mode"] = workspace_mode
        summary["analysis_timestamp_utc"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        if workspace_mode != "Single Optical":
            summary["scope_note"] = f"{workspace_mode} is a UI preview. The current result uses the single-image VQA MVP path."
        return result.answer, summary, result.evidence_markdown(), "● ANALYSIS COMPLETE — REVIEW EVIDENCE"
    except Exception as exc:
        return (
            "Analysis could not be completed. See the technical details below and verify model setup.",
            {"status": "analysis_error", "workspace_mode": workspace_mode, "detail": str(exc), "next_step": "Check model download, RAM/GPU availability, internet access, and inference mode."},
            "### Evidence\nNo model answer was generated. The uploaded image remains local to this session.",
            "● ANALYSIS ERROR — CHECK MODEL STATUS",
        )


def run_change_analysis(before: Image.Image | None, after: Image.Image | None):
    if before is None or after is None:
        return None, {"status": "waiting_for_images", "next_step": "Upload both before and after images."}
    result = compare_images(before, after)
    return result.heatmap, result.summary()


def run_feature_scout(image: Image.Image | None):
    if image is None:
        return {"status": "waiting_for_image", "next_step": "Upload a scene in the main workspace first."}
    return {"feature_scout": visual_feature_scout(image), "risk_readiness": preliminary_risk_flags(image)}


CSS = """
:root { --space:#060d1b; --panel:#0a1628; --line:#203854; --cyan:#00c8f0; --ink:#e9f5ff; --muted:#90a8bd; --green:#42d392; --amber:#f6c463; }
.gradio-container { background:var(--space)!important; color:var(--ink)!important; font-family:Inter,ui-sans-serif,system-ui,sans-serif!important; }
.gradio-container .prose, .gradio-container label, .gradio-container p { color:var(--ink)!important; } footer { display:none!important; }
#topbar { border-bottom:1px solid var(--line); margin:-16px -16px 24px; padding:15px 30px; background:rgba(6,13,27,.95); }
.topbar-inner { display:flex; justify-content:space-between; align-items:center; gap:18px; max-width:1500px; margin:auto; }
.brand { color:#fff; font:700 18px 'Arial Narrow',sans-serif; letter-spacing:.12em; } .brand b{color:var(--cyan)} .brand small { color:var(--muted); font:500 11px ui-monospace,monospace; letter-spacing:0; margin-left:10px; }
.nav { display:flex; gap:22px; color:var(--muted); font-size:12px; } .nav span:last-child{color:var(--green)}
.eyebrow { color:var(--cyan); font:700 11px ui-monospace,monospace; letter-spacing:.13em; }.hero { max-width:1500px; margin:0 auto 22px; padding:0 4px; }
.hero h1 { font:800 clamp(30px,5vw,62px) 'Arial Narrow',Impact,sans-serif; letter-spacing:.02em; line-height:.92; margin:9px 0 12px; }.hero h1 em { color:var(--cyan); font-style:normal; }
.hero p { color:var(--muted)!important; max-width:820px; margin:0; font-size:15px; line-height:1.6; }
.console { border:1px solid var(--line); border-radius:15px; padding:18px; background:linear-gradient(145deg,rgba(13,30,53,.95),rgba(7,18,33,.95)); box-shadow:0 22px 50px rgba(0,0,0,.24); }
.console h3 { margin:0 0 12px!important; font-size:12px!important; color:var(--muted)!important; letter-spacing:.1em; font-family:ui-monospace,monospace; }
.chip-row { display:flex; gap:7px; flex-wrap:wrap; margin:9px 0 12px; }.chip { border:1px solid #2b4a67; border-radius:999px; padding:5px 9px; color:#b8cce0; font:10px ui-monospace,monospace; }.chip.ok { border-color:#267f66; color:var(--green);}.chip.warn { border-color:#735d2e; color:var(--amber); }
.gradio-container .block, .gradio-container .form { background:transparent!important; }.gradio-container .wrap, .gradio-container .gr-box { border-radius:10px!important; }.gradio-container input, .gradio-container textarea { background:#071426!important; color:var(--ink)!important; border-color:#284661!important; }
.gradio-container button.primary { background:linear-gradient(120deg,#009fca,#00c8f0)!important; color:#02111d!important; border:0!important; font-weight:800!important; letter-spacing:.03em; }.gradio-container .tab-nav button { color:#b5cce0!important; }.gradio-container .tab-nav button.selected { color:var(--cyan)!important; border-color:var(--cyan)!important; }.gradio-container .image-container { background:#061222!important; border:1px dashed #2c5b7a!important; }
#answer-box textarea { font-size:16px!important; line-height:1.55!important; }.trace { border-left:2px solid var(--cyan); padding-left:12px; color:var(--muted); font:11px ui-monospace,monospace; line-height:1.8; }
@media (max-width:700px) { .nav {display:none}.topbar-inner{padding:0}.hero h1{font-size:36px} #topbar{padding:14px 16px;} }
"""

with gr.Blocks(theme=gr.themes.Base(), css=CSS, title="SatQuery AI | Vision-Language Intelligence") as demo:
    gr.HTML("""<div id='topbar'><div class='topbar-inner'><div class='brand'>SATQUERY <b>AI</b><small>v1.4.0 · MVP</small></div><div class='nav'><span>DOCUMENTATION</span><span>MODEL REGISTRY</span><span>● SYSTEMS NOMINAL</span></div></div></div>""")
    gr.HTML("""<section class='hero'><div class='eyebrow'>ISRO · SAC · VISION-LANGUAGE INTELLIGENCE PLATFORM</div><h1>ASK YOUR <em>SATELLITE</em><br>IMAGERY</h1><p>Natural-language analysis for aerial and satellite scenes, with transparent task routing and inspectable image evidence.</p></section>""")
    with gr.Row(equal_height=False):
        with gr.Column(scale=5, min_width=400, elem_classes="console"):
            gr.HTML("<h3>01 / CONFIGURE WORKSPACE</h3>")
            workspace_mode = gr.Radio(["Single Optical", "Single SAR", "Optical + SAR", "Bi-temporal"], value="Single Optical", label="Analysis modality")
            workspace_note = gr.Markdown(mode_note("Single Optical"))
            gr.HTML("<div class='chip-row'><span class='chip ok'>FORMAT · PNG / JPG</span><span class='chip ok'>IMAGE READY</span><span class='chip warn'>GEOREFERENCE · OPTIONAL</span></div>")
            image_input = gr.Image(type="pil", label="Scene input", height=360)
            gr.HTML("<div class='trace'>INPUT PIPELINE → RGB conversion → safe resize → pixel evidence extraction</div>")
        with gr.Column(scale=6, min_width=430, elem_classes="console"):
            gr.HTML("<h3>02 / ASK A QUESTION</h3>")
            question = gr.Textbox(label="Natural-language query", placeholder="e.g., Is there a road visible in this scene?", lines=4)
            inference_mode = gr.Radio(["Local Hugging Face", "Hosted Hugging Face API"], value="Hosted Hugging Face API" if settings.default_mode == "api" else "Local Hugging Face", label="Inference engine")
            submit = gr.Button("RUN ANALYSIS  →", variant="primary", size="lg")
            gr.Examples(examples=[["Is there a road visible in this scene?"], ["What is the dominant land cover?"], ["Are buildings visible?"], ["Is there a river or lake visible?"]], inputs=question, label="Suggested queries")
            runtime_status = gr.Textbox(value="● READY — WAITING FOR SCENE", label="Pipeline status", interactive=False)
    gr.HTML("<div style='height:18px'></div>")
    with gr.Accordion("PHASE 2 / CHANGE, FEATURE & RISK WORKBENCH", open=False):
        gr.Markdown("**Working baseline:** visual image comparison and RGB feature scouting. Uploads should depict the same area at a similar scale. Co-registration, geospatial area measurements, thermal fire evidence, and risk models are separate Phase 2 training tracks.")
        with gr.Row(equal_height=False):
            with gr.Column():
                before_image = gr.Image(type="pil", label="Before image")
            with gr.Column():
                after_image = gr.Image(type="pil", label="After image")
            with gr.Column():
                change_button = gr.Button("COMPARE SCENES", variant="primary")
                change_heatmap = gr.Image(label="Visual change heatmap", interactive=False)
                change_out = gr.JSON(label="Change summary")
        with gr.Row():
            feature_button = gr.Button("SCOUT VISIBLE FEATURES & RISK INPUTS")
            feature_out = gr.JSON(label="Feature/risk readiness")
    with gr.Row(equal_height=False):
        with gr.Column(scale=7, min_width=470, elem_classes="console"):
            gr.HTML("<h3>03 / ANALYSIS RESULT</h3>")
            with gr.Tabs():
                with gr.Tab("ANSWER"):
                    answer_out = gr.Textbox(label="Model response", lines=5, interactive=False, elem_id="answer-box")
                with gr.Tab("EVIDENCE"):
                    evidence_out = gr.Markdown("### Evidence\nSubmit an image and query to generate image-derived evidence.")
                with gr.Tab("TRACE"):
                    gr.Markdown("""<div class='trace'>01 · Route query using explainable keywords<br>02 · Prepare RGB image for selected VLM backend<br>03 · Generate response and expose model/backend metadata<br>04 · Return basic image facts (dimensions, EXIF when available, colour statistics)<br><br>Future pipelines: co-registration, SAR preprocessing, fusion, and validated change detection.</div>""")
        with gr.Column(scale=4, min_width=320, elem_classes="console"):
            gr.HTML("<h3>MODEL / TASK STATUS</h3>")
            route_out = gr.JSON(label="Execution record")
            gr.Markdown("""<div class='chip-row'><span class='chip ok'>VQA · ACTIVE</span><span class='chip warn'>CHANGE · ROADMAP</span><span class='chip warn'>SAR FUSION · ROADMAP</span></div><div class='trace'>Results are indicative VLM outputs, not validated remote-sensing measurements or operational intelligence.</div>""")
    workspace_mode.change(mode_note, workspace_mode, workspace_note)
    submit.click(analyze, [image_input, question, inference_mode, workspace_mode], [answer_out, route_out, evidence_out, runtime_status])
    question.submit(analyze, [image_input, question, inference_mode, workspace_mode], [answer_out, route_out, evidence_out, runtime_status])
    change_button.click(run_change_analysis, [before_image, after_image], [change_heatmap, change_out])
    feature_button.click(run_feature_scout, image_input, feature_out)

if __name__ == "__main__":
    demo.launch(server_name=settings.host, server_port=settings.port, show_error=True)
