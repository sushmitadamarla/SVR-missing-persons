import streamlit as st
import uuid
import os
import json
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks, extract_face_embedding  # ✅ ensure embedding extractor is imported
from pages.helper.data_models import PublicSubmissions
from pages.helper import db_queries

st.title("Report a Spotted Person")

image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if image:
    case_id = str(uuid.uuid4())
    img_path = f"./resources/{case_id}.jpg"
    with open(img_path, "wb") as f:
        f.write(image.read())

    st.image(image, width=200)
    st.info("Processing image...")

    # ✅ Convert image to numpy array
    img_array = image_obj_to_numpy(img_path)

    # ✅ Extract face mesh landmarks
    face_mesh = extract_face_mesh_landmarks(img_array)

    # ✅ Extract embedding using your InsightFace model (you already have this function)
    embedding_vector = extract_face_embedding(img_array)

    if face_mesh and embedding_vector is not None:
        with st.form("public_case_form"):
            location = st.text_input("Location Seen")
            mobile = st.text_input("Your Mobile Number")
            email = st.text_input("Your Email (optional)")
            birth_marks = st.text_input("Birth Marks (if any)")
            submit = st.form_submit_button("Submit")

            if submit:
                # ✅ Convert embedding to JSON string
                embedding_json = json.dumps(embedding_vector.tolist())

                # ✅ Create the PublicSubmissions object with embedding
                public_case = PublicSubmissions(
                    id=case_id,
                    submitted_by="public_user",
                    face_mesh=json.dumps(face_mesh),
                    embedding=embedding_json,   # ✅ store embedding
                    location=location,
                    mobile=mobile,
                    status="NF",
                    birth_marks=birth_marks,
                )

                # ✅ Save to database
                db_queries.new_public_case(public_case)
                st.success("Case submitted! We will try to match this with missing persons.")

    else:
        st.error("No valid face detected. Please upload a clear image showing a face.")
