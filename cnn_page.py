"""
Distraction Detector — Live Feed Edition
=========================================
ARCHITECTURE:
  - Background thread continuously reads webcam frames (no Streamlit involvement)
  - Frames stored in a thread-safe global queue/variable
  - Streamlit UI refreshes every ~1s via st_autorefresh to display latest frame
  - CNN analysis runs in background thread at configurable intervals
  - No st.rerun() needed — autorefresh handles UI updates cleanly

This solves the deadlock where:
  - st.camera_input holds the browser camera
  - OpenCV can't open the same camera
  - st.rerun() interrupts CNN mid-execution

Solution: OpenCV runs ENTIRELY in a daemon background thread.
          Streamlit only reads from shared state — never touches the camera.
"""

import os
import sys
import io
import time
import threading
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from PIL import Image
from typing import Optional
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "model", "distraction_cnn.keras")

EMOTION_TO_STATE = {
    "Angry":    {"state": "Distracted",       "emoji": "😤", "color": "#e17055"},
    "Disgust":  {"state": "Distracted",       "emoji": "🤢", "color": "#e17055"},
    "Fear":     {"state": "Distracted",       "emoji": "😨", "color": "#e17055"},
    "Surprise": {"state": "Distracted",       "emoji": "😲", "color": "#e17055"},
    "Happy":    {"state": "Focused",          "emoji": "😊", "color": "#00b894"},
    "Neutral":  {"state": "Focused",          "emoji": "😐", "color": "#00b894"},
    "Sad":      {"state": "Tired/Burned Out", "emoji": "😢", "color": "#fdcb6e"},
}
EMOTION_LABELS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL SHARED STATE  (lives outside Streamlit session — persists across reruns)
# ══════════════════════════════════════════════════════════════════════════════
st.write("Import test")

try:
    from cnn.cnn_model import load_model
    st.write("✅ Import works")
except Exception as e:
    st.error(f"❌ Import failed: {e}")
class CameraState:
    """Thread-safe container for camera + analysis state shared between
    the background capture thread and Streamlit's UI thread."""

    def __init__(self):
        self._lock           = threading.Lock()
        self.running         = False
        self.cam_index       = 0

        # Live frame (JPEG bytes) — updated every ~100ms by capture thread
        self.latest_frame    = None

        # Latest CNN result — updated after each analysis
        self.latest_result   = None
        self.latest_advice   = None

        # Timing
        self.last_analysis   = 0.0
        self.analysis_interval = 10        # seconds between analyses

        # Status
        self.status          = "idle"      # idle | capturing | analysing | error
        self.error_msg       = ""
        self.debug_msgs      = []

        # Session log (list of dicts)
        self.focus_log       = []

        # Control flags
        self._stop_event     = threading.Event()
        self._thread         = None

    # ── Thread-safe getters ──────────────────────────────────────────────────

    def get_frame(self):
        with self._lock:
            return self.latest_frame

    def get_result(self):
        with self._lock:
            return self.latest_result, self.latest_advice

    def get_log(self):
        with self._lock:
            return list(self.focus_log)

    def get_status(self):
        with self._lock:
            return self.status, self.error_msg

    def get_debug(self):
        with self._lock:
            return list(self.debug_msgs)

    def get_countdown(self):
        with self._lock:
            elapsed = time.time() - self.last_analysis
            remaining = max(0.0, self.analysis_interval - elapsed)
            pct = min(elapsed / max(self.analysis_interval, 1), 1.0)
            return remaining, pct

    # ── Thread-safe setters ──────────────────────────────────────────────────

    def set_frame(self, frame_bytes):
        with self._lock:
            self.latest_frame = frame_bytes

    def set_result(self, result, advice):
        with self._lock:
            self.latest_result = result
            self.latest_advice = advice
            if result:
                from datetime import datetime
                self.focus_log.append({
                    'time':       datetime.now().strftime('%H:%M:%S'),
                    'emotion':    result['emotion'],
                    'state':      result['study_state'],
                    'confidence': result['confidence'],
                })
                self.focus_log = self.focus_log[-30:]

    def set_status(self, status, error=""):
        with self._lock:
            self.status    = status
            self.error_msg = error

    def set_debug(self, msgs):
        with self._lock:
            self.debug_msgs = msgs

    def clear_log(self):
        with self._lock:
            self.focus_log    = []
            self.latest_result = None
            self.latest_advice = None
            self.last_analysis = 0.0

    def trigger_now(self):
        """Force immediate analysis on next capture cycle."""
        with self._lock:
            self.last_analysis = 0.0

    # ── Thread control ───────────────────────────────────────────────────────

    def start(self):
        if self._thread and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        self.running = True
        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
            name="CameraThread"
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.running = False

    def is_alive(self):
        return self._thread is not None and self._thread.is_alive()

    # ── Background capture loop ──────────────────────────────────────────────

    def _capture_loop(self):
        """
        Runs in background thread. Opens webcam once and keeps it open.
        Every ~100ms: grabs a frame and stores as JPEG for live display.
        Every N seconds: runs CNN analysis on current frame.
        """
        cap = self._open_camera()
        if cap is None:
            self.set_status("error", "❌ Could not open webcam. Check no other app is using it.")
            return

        self.set_status("capturing")

        try:
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.1)
                    continue

                # Convert BGR → RGB for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img       = Image.fromarray(frame_rgb)
                buf       = io.BytesIO()
                img.save(buf, format='JPEG', quality=80)
                self.set_frame(buf.getvalue())

                # Check if it's time to run CNN analysis
                with self._lock:
                    elapsed  = time.time() - self.last_analysis
                    interval = self.analysis_interval

                if elapsed >= interval:
                    self.set_status("analysing")
                    with self._lock:
                        self.last_analysis = time.time()

                    # Run CNN on current frame (grayscale for model)
                    result = self._run_cnn(frame_rgb)
                    if result:
                        advice = self._get_advice(result)
                        self.set_result(result, advice)

                    self.set_status("capturing")

                # ~30fps display, efficient sleep
                time.sleep(0.033)

        finally:
            cap.release()
            self.set_status("idle")

    def _open_camera(self):
        """Try to open webcam on indices 0, 1, 2 with fallback backends."""
        for idx in [0, 1, 2]:
            # Try DirectShow (Windows) first, then default
            for backend in [cv2.CAP_DSHOW, None]:
                cap = cv2.VideoCapture(idx, backend) if backend else cv2.VideoCapture(idx)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    # Warm-up: discard first 5 frames
                    for _ in range(5):
                        cap.read()
                    return cap
                cap.release()
        return None

    def _run_cnn(self, frame_rgb: np.ndarray) -> Optional[dict]:
        msgs = []
        try:
            model = _get_model()
            if model is None:
                msgs.append("❌ Model not loaded")
                self.set_debug(msgs)
                return None

            msgs.append(f"✅ Frame: {frame_rgb.shape}")

            face_img, face_found = _get_face(frame_rgb)
            msgs.append("✅ Face found" if face_found else "⚠️ No face — using full image")

            face_48 = np.array(
                Image.fromarray(face_img).resize((48, 48), Image.LANCZOS)
            ).astype('float32') / 255.0

            probs      = model.predict(face_48[np.newaxis, ..., np.newaxis], verbose=0)[0]
            idx        = int(np.argmax(probs))
            emotion    = EMOTION_LABELS[idx]
            confidence = float(probs[idx])
            state_info = EMOTION_TO_STATE.get(emotion, EMOTION_TO_STATE["Neutral"])

            msgs.append(f"✅ {emotion} ({confidence*100:.1f}%) → {state_info['state']}")
            self.set_debug(msgs)

            return {
                'emotion':           emotion,
                'study_state':       state_info['state'],
                'emoji':             state_info['emoji'],
                'color':             state_info['color'],
                'confidence':        confidence,
                'all_probabilities': {EMOTION_LABELS[i]: float(probs[i]) for i in range(7)},
                'face_found':        face_found,
            }
        except Exception as e:
            msgs.append(f"❌ CNN error: {e}")
            self.set_debug(msgs)
            return None

    def _get_advice(self, result: dict) -> str:
        try:
            import streamlit as st
            gemini = None
            for key in ['goal_agent', 'report_agent', 'planner_agent']:
                agent = st.session_state.get(key)
                if agent and hasattr(agent, 'model'):
                    gemini = agent.model
                    break
            if not gemini:
                raise ValueError("no gemini")
            return gemini.generate_content(
                f"You are an AI study coach.\n"
                f"Student focus check: {result['emotion']} ({result['confidence']*100:.0f}%) "
                f"→ {result['study_state']}\n"
                f"Write 2-3 short friendly sentences: acknowledge state, one tip, encouragement. No bullets."
            ).text.strip()
        except Exception:
            tips = {
                "Focused":          "Great focus! You're in the zone — keep it up. Take a short break every 25 minutes to stay sharp.",
                "Distracted":       "Something seems to have caught your attention. Try closing extra tabs and taking 3 deep breaths. You've got this!",
                "Tired/Burned Out": "You look a bit tired. A 10-minute break beats pushing through fatigue. Rest is part of studying smart.",
            }
            return tips.get(result['study_state'], tips["Focused"])


# ── Module-level singleton (persists across Streamlit reruns) ─────────────────
# Using st.session_state would reset on every hot-reload.
# A module-level variable persists for the lifetime of the process.
if '_camera_state' not in globals():
    _camera_state: CameraState = CameraState()


# ══════════════════════════════════════════════════════════════════════════════
# MODEL + FACE HELPERS  (module-level, not inside class)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Loading CNN model...")
def _get_model():
    try:
        from cnn.cnn_model import load_model
        return load_model(MODEL_PATH)
    except FileNotFoundError:
        return None


def _get_face(img_rgb: np.ndarray):
    gray    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, 1.1, 4, minSize=(40, 40))
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        return gray[y:y+h, x:x+w], True
    return gray, False


# ══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════════════════

def emotion_chart(probs: dict, detected: str) -> go.Figure:
    labels = [f"{e}  →  {EMOTION_TO_STATE.get(e,{}).get('state','?')}" for e in probs]
    values = [v * 100 for v in probs.values()]
    colors = [EMOTION_TO_STATE.get(e,{}).get('color','#667eea') if e == detected else '#dfe6e9'
              for e in probs]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in values],
        textposition='outside'
    ))
    fig.update_layout(
        title="CNN Output — Emotion Probabilities",
        xaxis=dict(range=[0, 120]),
        height=320,
        font=dict(family='Poppins', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=30, t=40, b=10)
    )
    return fig


def session_chart(log: list) -> go.Figure:
    score_map = {"Focused": 1, "Distracted": -1, "Tired/Burned Out": 0}
    scores = [score_map.get(e['state'], 0) for e in log]
    colors = ["#00b894" if s == 1 else ("#e17055" if s == -1 else "#fdcb6e") for s in scores]
    hover  = [f"#{i+1} {e['time']}: {e['emotion']} → {e['state']} ({e['confidence']*100:.0f}%)"
              for i, e in enumerate(log)]
    fig = go.Figure(go.Scatter(
        x=list(range(1, len(log)+1)), y=scores,
        mode='lines+markers',
        line=dict(color='#667eea', width=2),
        marker=dict(color=colors, size=12, line=dict(color='white', width=1)),
        fill='tozeroy', fillcolor='rgba(102,126,234,0.1)',
        hovertext=hover, hoverinfo='text'
    ))
    fig.update_layout(
        title="Focus Timeline",
        xaxis_title="Check #",
        yaxis=dict(tickvals=[-1,0,1],
                   ticktext=["😤 Distracted","😢 Tired","✅ Focused"],
                   range=[-1.6, 1.6]),
        height=260,
        font=dict(family='Poppins'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_cnn_page():
    global _camera_state

    st.markdown('<h1 class="main-header">🧠 Distraction Detector</h1>', unsafe_allow_html=True)

    # ── Model check ──────────────────────────────────────────────────────────
    model = _get_model()
    if model is None:
        st.error("⚠️ CNN model not found!")
        st.markdown("""
        1. Download `fer2013.csv` from [kaggle.com/datasets/deadskull7/fer2013](https://kaggle.com/datasets/deadskull7/fer2013)
        2. Place at `cnn/data/fer2013.csv`
        3. Run: `python cnn/cnn_model.py`
        """)
        col1, col2 = st.columns(2)
        with col1:
            epochs = st.slider("Epochs", 5, 50, 30)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Train Now", type="primary"):
                _train_in_app(epochs)
        return

    st.success("✅ CNN loaded!")
    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # CONTROLS
    # ════════════════════════════════════════════════════════════════════════
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 2, 1])

    with ctrl_col1:
        cam_active = _camera_state.is_alive()
        if cam_active:
            if st.button("⏹ Stop Camera", use_container_width=True, type="secondary"):
                _camera_state.stop()
                st.rerun()
        else:
            if st.button("▶ Start Live Camera", use_container_width=True, type="primary"):
                _camera_state.start()
                st.rerun()

    with ctrl_col2:
        interval = st.select_slider(
            "Analyse every",
            options=[5, 10, 15, 20, 30, 45, 60],
            value=_camera_state.analysis_interval,
            format_func=lambda x: f"{x} seconds"
        )
        _camera_state.analysis_interval = interval

    with ctrl_col3:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📸 Analyse Now", use_container_width=True):
                _camera_state.trigger_now()
        with col_b:
            if st.button("🗑 Clear Log", use_container_width=True):
                _camera_state.clear_log()

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # LIVE FEED + RESULT  (side by side)
    # ════════════════════════════════════════════════════════════════════════
    feed_col, result_col = st.columns([1, 1])

    with feed_col:
        st.markdown("### 📷 Live Camera Feed")

        status, error_msg = _camera_state.get_status()

        if not _camera_state.is_alive():
            st.markdown(
                "<div style='border:2px dashed #dee2e6; border-radius:12px;"
                "padding:4rem; text-align:center; color:#adb5bd'>"
                "▶ Press <b>Start Live Camera</b> to begin<br><br>"
                "🔒 The browser camera widget is NOT used —<br>"
                "OpenCV captures directly from your webcam."
                "</div>",
                unsafe_allow_html=True
            )
        elif status == "error":
            st.error(error_msg or "Camera error")
        else:
            frame_bytes = _camera_state.get_frame()
            if frame_bytes:
                st.image(frame_bytes, use_container_width=True, channels="RGB")
            else:
                st.info("⏳ Waiting for first frame...")

            # Status badge
            if status == "analysing":
                st.markdown(
                    "<div style='background:#fdcb6e22; border-left:4px solid #fdcb6e;"
                    "padding:0.5rem 1rem; border-radius:8px; margin-top:0.5rem'>"
                    "🧠 <b>Analysing emotion...</b></div>",
                    unsafe_allow_html=True
                )
            else:
                remaining, pct = _camera_state.get_countdown()
                st.progress(pct)
                st.caption(f"⏱ Next analysis in {remaining:.0f}s")

    with result_col:
        st.markdown("### 📊 Latest Emotion")
        result, advice = _camera_state.get_result()

        if result:
            color = result['color']
            st.markdown(f"""
            <div style="background:{color}22; border-left:6px solid {color};
                        padding:1.5rem; border-radius:14px; margin-bottom:1rem">
                <div style="font-size:3.5rem; line-height:1">{result['emoji']}</div>
                <h2 style="color:{color}; margin:0.4rem 0 0.2rem">{result['study_state']}</h2>
                <p style="margin:0; font-size:0.95rem">
                    <b>{result['emotion']}</b> — {result['confidence']*100:.1f}% confidence<br>
                    <span style="opacity:0.6; font-size:0.82rem">
                        {'✅ Face detected' if result['face_found'] else '⚠️ No face — full image used'}
                    </span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if advice:
                st.info(f"💡 {advice}")

            st.plotly_chart(
                emotion_chart(result['all_probabilities'], result['emotion']),
                use_container_width=True,
                key=f"echart_{result['emotion']}_{result['confidence']:.4f}"
            )
        else:
            st.markdown(
                "<div style='border:2px dashed #dee2e6; padding:3rem;"
                "border-radius:14px; text-align:center; color:#adb5bd'>"
                "📊 Analysis results will appear here</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # SESSION LOG
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("### 📈 Session Log")
    log = _camera_state.get_log()

    if log:
        total      = len(log)
        focused    = sum(1 for e in log if e['state'] == 'Focused')
        distracted = sum(1 for e in log if e['state'] == 'Distracted')
        tired      = sum(1 for e in log if e['state'] == 'Tired/Burned Out')

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Checks",  total)
        c2.metric("✅ Focused",    focused,    f"{focused/total*100:.0f}%")
        c3.metric("❌ Distracted", distracted, f"{distracted/total*100:.0f}%")
        c4.metric("⚠️ Tired",      tired,      f"{tired/total*100:.0f}%")

        st.plotly_chart(session_chart(log), use_container_width=True)

        st.markdown("**Recent Checks:**")
        for entry in reversed(log[-5:]):
            info  = EMOTION_TO_STATE.get(entry['emotion'], {})
            color = info.get('color', '#667eea')
            emoji = info.get('emoji', '❓')
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:1rem;"
                f"padding:0.4rem 0.8rem;margin:0.2rem 0;"
                f"background:{color}18;border-radius:8px;border-left:3px solid {color}'>"
                f"<span style='font-size:1.3rem'>{emoji}</span>"
                f"<span><b>{entry['state']}</b> — {entry['emotion']} ({entry['confidence']*100:.0f}%)</span>"
                f"<span style='margin-left:auto;opacity:0.5;font-size:0.85rem'>{entry['time']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        if total >= 3:
            if distracted / total >= 0.6:
                st.error("⚠️ **High distraction** — over 60% of checks showed distraction.")
            elif focused / total >= 0.7:
                st.success("🎉 **Excellent session!** — Focused over 70% of the time!")

        with st.expander("📋 Full Log"):
            import pandas as pd
            df = pd.DataFrame(log)
            df['confidence'] = df['confidence'].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(df, use_container_width=True)

        with st.expander("🔧 Debug"):
            status, err = _camera_state.get_status()
            remaining, pct = _camera_state.get_countdown()
            st.text(f"Camera alive: {_camera_state.is_alive()}")
            st.text(f"Status: {status} {err}")
            st.text(f"Next analysis in: {remaining:.1f}s")
            st.text(f"Log entries: {total}")
            for m in _camera_state.get_debug():
                st.text(m)
    else:
        st.info("Your focus timeline will appear here after the first analysis.")

    # ════════════════════════════════════════════════════════════════════════
    # AUTO-REFRESH  (only when camera is running — keeps UI live without rerun)
    # ════════════════════════════════════════════════════════════════════════
    if _camera_state.is_alive():
        # Refresh every 500ms for smooth live feed + countdown update
        # This is the ONLY mechanism driving UI updates — no st.rerun() anywhere
        st_autorefresh(interval=500, limit=None, key="live_feed_refresh")


# ══════════════════════════════════════════════════════════════════════════════
# TRAIN HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _train_in_app(epochs):
    try:
        from cnn.cnn_model import train_model
        with st.spinner(f"Training {epochs} epochs..."):
            _, _, acc = train_model(epochs=epochs, save_path=MODEL_PATH)
        st.success(f"✅ Done! Accuracy: {acc*100:.2f}%")
        st.rerun()
    except FileNotFoundError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Training failed: {e}")