import PIL
import numpy as np
import streamlit as st
import cv2
import mediapipe as mp
from insightface.app import FaceAnalysis

# ------------------ Initialize Models ------------------
mp_face_mesh = mp.solutions.face_mesh

# ✅ Initialize InsightFace model once
try:
    face_app = FaceAnalysis(name="buffalo_l")
    face_app.prepare(ctx_id=0)  # use GPU if available, else CPU
except Exception as e:
    st.warning(f"⚠️ Could not initialize InsightFace model: {e}")
    face_app = None


# ------------------ Utility: Image Conversion ------------------
def image_obj_to_numpy(image_obj) -> np.ndarray:
    """Convert Streamlit-uploaded image object or file path to RGB numpy array."""
    if isinstance(image_obj, str):
        image = PIL.Image.open(image_obj)
    else:
        image = PIL.Image.open(image_obj)
    return np.array(image.convert("RGB"))  # 🔥 ensures always 3-channel RGB


# ------------------ Face Mesh Extraction ------------------
def extract_face_mesh_landmarks(image):
    """Extract face mesh landmarks using MediaPipe Face Mesh."""
    try:
        # 🟢 Ensure image is RGB
        if len(image.shape) == 2:  # grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            results = face_mesh.process(image)

            if not results.multi_face_landmarks:
                st.error("⚠️ Couldn't find face mesh in image. Please try another image.")
                return None

            face_landmarks = results.multi_face_landmarks[0].landmark
            return [(lm.x, lm.y, lm.z) for lm in face_landmarks]

    except Exception as e:
        st.error(f"⚠️ Face mesh extraction failed: {e}")
        return None


# ------------------ Face Embedding Extraction ------------------
def extract_face_embedding(image: np.ndarray):
    """
    Extract face embedding using InsightFace.
    Returns a 512-D numpy array if successful, else None.
    """
    if face_app is None:
        st.error("❌ Face recognition model not loaded properly.")
        return None

    try:
        # 🟢 Convert image safely to BGR (required by InsightFace)
        if len(image.shape) == 2:  # grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        bgr_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        faces = face_app.get(bgr_img)
        if len(faces) == 0:
            st.error("⚠️ No face detected. Please upload a clear, front-facing image.")
            return None

        # ✅ Extract first face embedding (512-D)
        embedding = faces[0].embedding
        return np.array(embedding, dtype=np.float32)

    except Exception as e:
        st.error(f"⚠️ Error extracting embedding: {e}")
        return None