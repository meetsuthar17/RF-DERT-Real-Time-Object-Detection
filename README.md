# RF-DERT Real-Time Object Detection

A lightweight object detection project built around the RF-DETR model. This repository includes a FastAPI backend for image/video inference and a Streamlit frontend for easy demo interaction.

## Features

- Real-time object detection using RF-DETR
- FastAPI endpoints for image and video prediction
- Streamlit interface for upload and preview
- Annotated output returned as JPEG or MP4

## Included files

- `app.py` — Streamlit frontend and UI styling
- `dert.py` — FastAPI backend with model inference and annotation

## Requirements

- Python 3.10+
- `fastapi`
- `streamlit`
- `uvicorn`
- `Pillow`
- `opencv-python`
- `supervision`
- `rfdetr`
- `numpy`

## Install

```bash
pip install fastapi streamlit uvicorn Pillow opencv-python supervision rfdetr numpy
```

## Run

### Start the FastAPI backend

```bash
uvicorn dert:app --reload
```

### Start the Streamlit app

```bash
streamlit run app.py
```

## API Endpoints

- `POST /predict/image` — upload an image and receive an annotated JPEG
- `POST /predict/image/json` — upload an image and receive raw detection JSON
- `POST /predict/video` — upload a video and receive an annotated MP4

## Notes

- The project is designed for object detection, not diabetes prediction.
- The repository contains only the necessary project files, excluding `venv` and cached Python files.
