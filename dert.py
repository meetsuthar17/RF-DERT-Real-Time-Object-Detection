from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES
from PIL import Image
import supervision as sv
import numpy as np
import io
import cv2
import tempfile
import os
 
app = FastAPI()
 
# Load RF-DETR model
model = RFDETRBase()
 
# Annotators
box_annotator = sv.BoxAnnotator(thickness=2)
label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)
 
 
def annotate_image(image: Image.Image, detections: sv.Detections) -> bytes:
    """Draw boxes and labels on image, return as JPEG bytes."""
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
 
    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]
 
    annotated = box_annotator.annotate(scene=frame, detections=detections)
    annotated = label_annotator.annotate(scene=annotated, detections=detections, labels=labels)
 
    _, buffer = cv2.imencode(".jpg", annotated)
    return buffer.tobytes()
 
 
@app.get("/")
def home():
    return {"message": "RF-DETR API Running"}
 
 
# ── IMAGE: returns annotated image ──────────────────────────────────────────
@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return JSONResponse(content={"error": "Only image files allowed"}, status_code=400)
 
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
 
        detections = model.predict(image, threshold=0.5)
        annotated_bytes = annotate_image(image, detections)
 
        return StreamingResponse(
            io.BytesIO(annotated_bytes),
            media_type="image/jpeg",
            headers={"X-Detection-Count": str(len(detections))}
        )
 
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
 
 
# ── IMAGE: returns JSON with box coords + labels (if you need raw data) ─────
@app.post("/predict/image/json")
async def predict_image_json(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return JSONResponse(content={"error": "Only image files allowed"}, status_code=400)
 
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
 
        detections = model.predict(image, threshold=0.5)
 
        results = []
        for i in range(len(detections)):
            x1, y1, x2, y2 = detections.xyxy[i].tolist()
            results.append({
                "class_id": int(detections.class_id[i]),
                "class_name": COCO_CLASSES[int(detections.class_id[i])],
                "confidence": round(float(detections.confidence[i]), 4),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })
 
        return JSONResponse(content={"type": "image", "detections": results})
 
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
 
 
# ── VIDEO: returns annotated video ──────────────────────────────────────────
@app.post("/predict/video")
async def predict_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        return JSONResponse(content={"error": "Only video files allowed"}, status_code=400)
 
    try:
        # Save input video to temp file
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_in.write(await file.read())
        temp_in.close()
 
        temp_out_path = temp_in.name.replace(".mp4", "_annotated.mp4")
 
        cap = cv2.VideoCapture(temp_in.name)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_out_path, fourcc, fps, (width, height))
 
        frame_count = 0
        last_detections = None  # reuse detections for skipped frames
 
        while True:
            ret, frame = cap.read()
            if not ret:
                break
 
            # Run model every 5th frame; reuse last result for others
            if frame_count % 5 == 0:
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                last_detections = model.predict(pil_image, threshold=0.5)
 
            if last_detections is not None and len(last_detections) > 0:
                labels = [
                    f"{COCO_CLASSES[class_id]} {conf:.2f}"
                    for class_id, conf in zip(last_detections.class_id, last_detections.confidence)
                ]
                frame = box_annotator.annotate(scene=frame, detections=last_detections)
                frame = label_annotator.annotate(scene=frame, detections=last_detections, labels=labels)
 
            out.write(frame)
            frame_count += 1
 
        cap.release()
        out.release()
 
        # Stream annotated video back
        def video_stream():
            with open(temp_out_path, "rb") as f:
                yield from f
            os.unlink(temp_in.name)
            os.unlink(temp_out_path)
 
        return StreamingResponse(
            video_stream(),
            media_type="video/mp4",
            headers={"X-Total-Frames": str(frame_count)}
        )
 
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)