import numpy as np
import cv2
from insightface.app import FaceAnalysis

# Initialize InsightFace model
model = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))

def extract_embedding(image_np):
    """
    Extract 512-d InsightFace embedding from a BGR/RGBA image.
    """
    try:
        # 🟢 Ensure image is 3-channel RGB
        if image_np.shape[2] == 4:  # RGBA image
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
        elif image_np.shape[2] == 1:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)

        # Detect face
        faces = model.get(image_np)
        if not faces:
            print("[WARN] No face detected.")
            return None

        # Extract normalized embedding
        embedding = faces[0].embedding
        embedding = embedding / np.linalg.norm(embedding)
        print("[DEBUG] Extracted embedding shape:", embedding.shape)
        print("[DEBUG] First 5 values:", embedding[:5])

        return embedding

    except Exception as e:
        print(f"[ERROR] extract_embedding failed: {e}")
        return None
