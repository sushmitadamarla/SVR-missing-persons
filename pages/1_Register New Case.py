import uuid
import numpy as np
import streamlit as st
import json
import base64

from pages.helper.data_models import RegisteredCases
from pages.helper import db_queries
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks
from pages.helper.streamlit_helpers import require_login
from pages.helper.face_recognition_model import extract_embedding  # ✅ InsightFace model

# -------------------- #
# Streamlit Page Setup #
# -------------------- #
st.set_page_config(page_title="Register New Case")

def image_to_base64(image):
    return base64.b64encode(image).decode("utf-8")


# ----------------------------- #
#     MAIN STREAMLIT LOGIC      #
# ----------------------------- #
if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    user = st.session_state.user
    st.title("Register New Case")

    image_col, form_col = st.columns(2)
    image_obj = None
    save_flag = 0
    embedding_str = None
    face_mesh = None
    unique_id = None

    with image_col:
        # 🖼️ Upload Image
        image_obj = st.file_uploader(
            "Upload Image of Missing Person",
            type=["jpg", "jpeg", "png"],
            key="new_case"
        )

        if image_obj:
            unique_id = str(uuid.uuid4())
            uploaded_file_path = f"./resources/{unique_id}.jpg"

            # Save uploaded image
            with open(uploaded_file_path, "wb") as output_temporary_file:
                output_temporary_file.write(image_obj.read())

            # Process Image
            with st.spinner("Processing image and extracting facial features..."):
                st.image(image_obj, caption="Uploaded Image", use_container_width=False)
                image_numpy = image_obj_to_numpy(uploaded_file_path)

                # ✅ Extract 512-D InsightFace embedding
                embedding = extract_embedding(image_numpy)
                if embedding is None:
                    st.error("⚠️ No face detected. Please upload a clear image.")
                    st.stop()

                # Convert embedding to JSON string for DB
                embedding_str = json.dumps(embedding.tolist())

                # (Optional) MediaPipe face mesh landmarks
                face_mesh = extract_face_mesh_landmarks(image_numpy)

    # ------------------------- #
    # Form for case details
    # ------------------------- #
    if image_obj and embedding_str:
        with form_col.form(key="new_case"):
            st.subheader("Case Information")

            name = st.text_input("Name")
            fathers_name = st.text_input("Father's Name")
            age = st.number_input("Age", min_value=3, max_value=100, value=10, step=1)
            mobile_number = st.text_input("Complainant Mobile Number")
            address = st.text_input("Address")
            adhaar_card = st.text_input("Aadhaar Card Number")
            birthmarks = st.text_input("Birth Mark / Identifiable Features")
            last_seen = st.text_input("Last Seen Location")
            description = st.text_area("Description (optional)")

            complainant_name = st.text_input("Complainant Name")
            complainant_phone = st.text_input("Complainant Alternate Phone")

            submit_bt = st.form_submit_button("Save Case")

            if submit_bt:
                new_case_details = RegisteredCases(
                    id=unique_id,
                    submitted_by=user,
                    name=name,
                    fathers_name=fathers_name,
                    age=age,
                    complainant_mobile=mobile_number,
                    complainant_name=complainant_name,
                    face_mesh=json.dumps(face_mesh) if face_mesh else None,
                    embedding=embedding_str,  # ✅ Store embedding
                    adhaar_card=adhaar_card,
                    birth_marks=birthmarks,
                    address=address,
                    last_seen=last_seen,
                    status="NF",  # Not Found
                    matched_with="",
                )

                db_queries.register_new_case(new_case_details)
                save_flag = 1

        if save_flag:
            st.success("✅ Case Registered Successfully!")

else:
    st.write("You don't have access to this page")
