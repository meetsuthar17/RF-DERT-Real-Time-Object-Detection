import streamlit as st
import requests
import io
import json
import time
from PIL import Image
import tempfile
import os

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RF-DETR Detection",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0a;
    color: #e8e4d9;
}

.stApp {
    background: #0a0a0a;
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Header */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3.5rem;
    letter-spacing: -0.03em;
    line-height: 1;
    color: #e8e4d9;
    margin: 0;
}

.hero-accent {
    color: #c8ff00;
}

.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 300;
    color: #666;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* Divider */
.acid-line {
    height: 1px;
    background: linear-gradient(90deg, #c8ff00, transparent);
    margin: 1.5rem 0;
}

/* Upload Zone */
.upload-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* Metric Cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.metric-card {
    background: #141414;
    border: 1px solid #222;
    border-left: 3px solid #c8ff00;
    padding: 1rem 1.2rem;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #c8ff00;
    line-height: 1;
}

.metric-label {
    font-size: 0.65rem;
    color: #555;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* Detection Table */
.det-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.75rem;
    margin-top: 1rem;
}

.det-table th {
    text-align: left;
    color: #555;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid #222;
}

.det-table td {
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid #1a1a1a;
    color: #e8e4d9;
    font-family: 'DM Mono', monospace;
}

.det-table tr:hover td {
    background: #141414;
}

.conf-bar {
    height: 3px;
    background: #1a1a1a;
    border-radius: 2px;
    margin-top: 4px;
}

.conf-fill {
    height: 100%;
    background: #c8ff00;
    border-radius: 2px;
}

/* Status badge */
.status-ok {
    display: inline-block;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c8ff00;
    border: 1px solid #c8ff00;
    padding: 2px 8px;
}

.status-err {
    display: inline-block;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #ff4444;
    border: 1px solid #ff4444;
    padding: 2px 8px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 1px solid #1a1a1a;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Streamlit widget overrides */
.stSlider > div > div > div > div {
    background: #c8ff00 !important;
}

div[data-baseweb="select"] {
    background: #141414 !important;
    border-color: #2a2a2a !important;
}

.stButton > button {
    background: #c8ff00 !important;
    color: #0a0a0a !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
}

.stButton > button:hover {
    background: #d4ff33 !important;
    transform: translateY(-1px) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #111 !important;
    border: 1px dashed #2a2a2a !important;
    border-radius: 0 !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #c8ff00 !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid #222 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #555 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 1.5rem !important;
}

.stTabs [aria-selected="true"] {
    color: #c8ff00 !important;
    border-bottom: 2px solid #c8ff00 !important;
}

/* Progress / spinner */
.stSpinner > div {
    border-top-color: #c8ff00 !important;
}

/* Image display */
[data-testid="stImage"] img {
    border: 1px solid #1a1a1a;
}

/* Video */
video {
    border: 1px solid #1a1a1a;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ── API Config ────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:2rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#e8e4d9;letter-spacing:-0.02em'>
            RF-DETR
        </div>
        <div style='font-size:0.6rem;color:#555;letter-spacing:0.15em;text-transform:uppercase;margin-top:2px'>
            Real-Time Detection
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="acid-line"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.65rem;color:#555;letter-spacing:0.1em;text-transform:uppercase">API Endpoint</p>', unsafe_allow_html=True)
    api_url = st.text_input("", value=API_BASE, label_visibility="collapsed")

    st.markdown('<div class="acid-line"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.65rem;color:#555;letter-spacing:0.1em;text-transform:uppercase">Confidence Threshold</p>', unsafe_allow_html=True)
    threshold = st.slider("", min_value=0.1, max_value=1.0, value=0.5, step=0.05, label_visibility="collapsed")
    st.markdown(f'<p style="font-size:0.7rem;color:#c8ff00;font-family:DM Mono,monospace">{threshold:.2f}</p>', unsafe_allow_html=True)

    st.markdown('<div class="acid-line"></div>', unsafe_allow_html=True)

    # API Health Check
    st.markdown('<p style="font-size:0.65rem;color:#555;letter-spacing:0.1em;text-transform:uppercase">API Status</p>', unsafe_allow_html=True)
    if st.button("Check Connection"):
        try:
            r = requests.get(f"{api_url}/", timeout=3)
            if r.status_code == 200:
                st.markdown('<span class="status-ok">● Online</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-err">● Error</span>', unsafe_allow_html=True)
        except:
            st.markdown('<span class="status-err">● Offline</span>', unsafe_allow_html=True)

    st.markdown('<div class="acid-line"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.6rem;color:#333;letter-spacing:0.08em">RF-DETR · COCO 80 Classes<br>Real-time object detection</p>', unsafe_allow_html=True)


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 2rem">
    <h1 class="hero-title">OBJECT<br><span class="hero-accent">DETECTION.</span></h1>
    <p class="hero-sub">RF-DETR · Real-Time Transformer Detection</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="acid-line"></div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_image, tab_video, tab_json = st.tabs(["Image Detection", "Video Detection", "Raw JSON Output"])


# ═══════════════════════════════════════════
# TAB 1 - IMAGE
# ═══════════════════════════════════════════
with tab_image:
    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<p class="upload-hint">Upload Image</p>', unsafe_allow_html=True)
        img_file = st.file_uploader(
            "",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            key="img_uploader",
            label_visibility="collapsed"
        )

        if img_file:
            st.image(img_file, caption="Original", use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            run_img = st.button("Run Detection", key="run_image")

    with col_result:
        if img_file and run_img:
            with st.spinner("Detecting..."):
                start = time.time()
                try:
                    img_file.seek(0)
                    files = {"file": (img_file.name, img_file.read(), img_file.type)}
                    response = requests.post(
                        f"{api_url}/predict/image",
                        files=files,
                        timeout=30
                    )
                    elapsed = time.time() - start

                    if response.status_code == 200:
                        result_img = Image.open(io.BytesIO(response.content))
                        detection_count = int(response.headers.get("X-Detection-Count", 0))

                        # Metrics
                        st.markdown(f"""
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">{detection_count}</div>
                                <div class="metric-label">Objects Found</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{elapsed:.2f}s</div>
                                <div class="metric-label">Inference Time</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{threshold:.2f}</div>
                                <div class="metric-label">Threshold</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.image(result_img, caption="Annotated Result", use_container_width=True)

                        # Download button
                        buf = io.BytesIO()
                        result_img.save(buf, format="JPEG", quality=95)
                        st.download_button(
                            label="Download Result",
                            data=buf.getvalue(),
                            file_name=f"rfdetr_{img_file.name}",
                            mime="image/jpeg"
                        )

                    else:
                        st.markdown(f'<span class="status-err">Error {response.status_code}</span>', unsafe_allow_html=True)
                        st.code(response.text)

                except requests.exceptions.ConnectionError:
                    st.markdown('<span class="status-err">Cannot connect to API. Is FastAPI running?</span>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<span class="status-err">Error: {str(e)}</span>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 2 - VIDEO
# ═══════════════════════════════════════════
with tab_video:
    col_v1, col_v2 = st.columns([1, 1], gap="large")

    with col_v1:
        st.markdown('<p class="upload-hint">Upload Video</p>', unsafe_allow_html=True)
        vid_file = st.file_uploader(
            "",
            type=["mp4", "mov", "avi", "mkv"],
            key="vid_uploader",
            label_visibility="collapsed"
        )

        if vid_file:
            st.video(vid_file)
            st.markdown(f"""
            <p style="font-size:0.7rem;color:#555;font-family:DM Mono,monospace">
                {vid_file.name} · {vid_file.size / (1024*1024):.1f} MB
            </p>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            run_vid = st.button("Run Detection", key="run_video")

    with col_v2:
        if vid_file and run_vid:
            progress_bar = st.progress(0, text="Uploading video...")
            with st.spinner("Processing video... this may take a while"):
                start = time.time()
                try:
                    vid_file.seek(0)
                    progress_bar.progress(20, text="Sending to API...")

                    files = {"file": (vid_file.name, vid_file.read(), vid_file.type)}
                    response = requests.post(
                        f"{api_url}/predict/video",
                        files=files,
                        timeout=300
                    )
                    elapsed = time.time() - start
                    progress_bar.progress(90, text="Rendering output...")

                    if response.status_code == 200:
                        total_frames = int(response.headers.get("X-Total-Frames", 0))
                        progress_bar.progress(100, text="Done.")

                        st.markdown(f"""
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">{total_frames}</div>
                                <div class="metric-label">Total Frames</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{elapsed:.1f}s</div>
                                <div class="metric-label">Process Time</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{len(response.content)/(1024*1024):.1f}MB</div>
                                <div class="metric-label">Output Size</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.video(io.BytesIO(response.content))

                        st.download_button(
                            label="Download Annotated Video",
                            data=response.content,
                            file_name=f"rfdetr_{vid_file.name}",
                            mime="video/mp4"
                        )

                    else:
                        progress_bar.empty()
                        st.markdown(f'<span class="status-err">Error {response.status_code}</span>', unsafe_allow_html=True)
                        st.code(response.text)

                except requests.exceptions.ConnectionError:
                    progress_bar.empty()
                    st.markdown('<span class="status-err">Cannot connect to API. Is FastAPI running?</span>', unsafe_allow_html=True)
                except Exception as e:
                    progress_bar.empty()
                    st.markdown(f'<span class="status-err">Error: {str(e)}</span>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 3 - JSON OUTPUT
# ═══════════════════════════════════════════
with tab_json:
    st.markdown('<p class="upload-hint">Upload Image for Raw JSON Detection Data</p>', unsafe_allow_html=True)

    json_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png", "webp"],
        key="json_uploader",
        label_visibility="collapsed"
    )

    if json_file:
        col_j1, col_j2 = st.columns([1, 1], gap="large")

        with col_j1:
            st.image(json_file, use_container_width=True)
            run_json = st.button("Get JSON Data", key="run_json")

        with col_j2:
            if run_json:
                with st.spinner("Running..."):
                    try:
                        json_file.seek(0)
                        files = {"file": (json_file.name, json_file.read(), json_file.type)}
                        response = requests.post(
                            f"{api_url}/predict/image/json",
                            files=files,
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()
                            detections = data.get("detections", [])

                            if detections:
                                # Detection table
                                rows = ""
                                for d in detections:
                                    conf = d["confidence"]
                                    bar_width = int(conf * 100)
                                    rows += f"""
                                    <tr>
                                        <td>{d['class_name']}</td>
                                        <td>
                                            {conf:.3f}
                                            <div class="conf-bar"><div class="conf-fill" style="width:{bar_width}%"></div></div>
                                        </td>
                                        <td style="color:#555;font-size:0.65rem">
                                            ({d['bbox']['x1']:.0f}, {d['bbox']['y1']:.0f})<br>
                                            ({d['bbox']['x2']:.0f}, {d['bbox']['y2']:.0f})
                                        </td>
                                    </tr>
                                    """

                                st.markdown(f"""
                                <table class="det-table">
                                    <thead>
                                        <tr>
                                            <th>Class</th>
                                            <th>Confidence</th>
                                            <th>BBox (x1,y1) (x2,y2)</th>
                                        </tr>
                                    </thead>
                                    <tbody>{rows}</tbody>
                                </table>
                                """, unsafe_allow_html=True)

                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown('<p style="font-size:0.6rem;color:#555;letter-spacing:0.1em;text-transform:uppercase">Raw JSON</p>', unsafe_allow_html=True)
                            st.json(data)

                            st.download_button(
                                label="Download JSON",
                                data=json.dumps(data, indent=2),
                                file_name="rfdetr_detections.json",
                                mime="application/json"
                            )

                        else:
                            st.markdown(f'<span class="status-err">Error {response.status_code}</span>', unsafe_allow_html=True)
                            st.code(response.text)

                    except requests.exceptions.ConnectionError:
                        st.markdown('<span class="status-err">Cannot connect to API. Is FastAPI running?</span>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<span class="status-err">Error: {str(e)}</span>', unsafe_allow_html=True)