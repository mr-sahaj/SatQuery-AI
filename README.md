# SatQuery-AI
SatQuery AI is an interactive, agentic vision-language assistant for analysing single and paired remote-sensing images through natural-language queries. It is not intended to be a generic chatbot: the solution must be adapted to remote-sensing imagery and route queries to suitable specialist models/tools.
# 🛰️ SatQuery AI

### An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis

> **SIH 2026 — SIH26167**
>
> Building an agentic AI system that allows users to analyze satellite imagery using natural-language queries.

---

## 🌍 Overview

**SatQuery AI** is an interactive, agentic Vision-Language system designed to make remote-sensing image analysis accessible through natural-language queries.

Instead of requiring users to manually select different models and GIS workflows for different tasks, SatQuery interprets the user's query, identifies the required analysis, selects the appropriate AI models/tools, executes the workflow, and returns an **evidence-grounded and auditable response**.

The system is designed to work with:

- 🛰️ Optical / Multispectral satellite imagery
- 📡 SAR imagery
- 🔄 Bi-temporal satellite imagery
- 🔗 Co-registered Optical + SAR image pairs
- 💬 Natural-language queries

---

## 🎯 Problem

Remote-sensing analysis often requires users to understand:

- Satellite imagery characteristics
- Different image modalities
- GIS workflows
- Multiple AI models
- Model-specific parameters
- Different tools for different analysis tasks

Existing solutions are often **task-specific**.

A user may need one model for VQA, another for change detection, another for object detection, and another for image captioning.

### SatQuery aims to provide a unified interface.

Instead of asking:

> "Which model should I use?"

The user simply asks:

> **"What changed in this area between the two images?"**

SatQuery determines the appropriate analysis pipeline automatically.

---

# 🚀 Key Features

## 1. 🧠 Natural Language Interaction

Users can interact with satellite imagery using ordinary language.

Example:

```text
"What major changes occurred between these two images?"
