import yaml
import base64
import streamlit as st
from yaml import SafeLoader
import streamlit_authenticator as stauth

from pages.helper import db_queries
from pages.helper.utils import image_obj_to_numpy, extract_face_mesh_landmarks
from pages.helper.data_models import PublicSubmissions
import uuid
import json
import os


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

try:
    with open("login_config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'login_config.yml' not found")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

authenticator.login(location="main")

if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")

    st.session_state["login_status"] = True
    user_info = config["credentials"]["usernames"][st.session_state["username"]]
    st.session_state["user"] = user_info["name"]

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Dashboard", "Submit Sighting"])

    if page == "Dashboard":
        st.write(
            f'<p style="color:grey; text-align:left; font-size:45px">{user_info["name"]}</p>',
            unsafe_allow_html=True,
        )
        st.write(
            f'<p style="color:grey; text-align:left; font-size:20px">{user_info["area"]}, {user_info["city"]}</p>',
            unsafe_allow_html=True,
        )
        st.write(
            f'<p style="color:grey; text-align:left; font-size:20px">{user_info["role"]}</p>',
            unsafe_allow_html=True,
        )
        st.write("---")

        found_cases = db_queries.get_registered_cases_count(user_info["name"], "F")
        non_found_cases = db_queries.get_registered_cases_count(user_info["name"], "NF")

        found_col, not_found_col = st.columns(2)
        found_col.metric("Found Cases Count", value=len(found_cases))
        not_found_col.metric("Not Found Cases Count", value=len(non_found_cases))

    elif page == "Submit Sighting":
        st.title("Report a Spotted Person")

        image_obj = st.file_uploader("Upload Spotted Person Image", type=["jpg", "jpeg", "png"])
        if image_obj:
            image_numpy = image_obj_to_numpy(image_obj)
            st.image(image_obj)
            face_mesh = extract_face_mesh_landmarks(image_numpy)

            if face_mesh:
                location = st.text_input("Location (Where person was seen)")
                mobile = st.text_input("Your Mobile Number")
                email = st.text_input("Your Email (optional)")
                birth_marks = st.text_input("Birth Marks or Identifiable Marks")
                status = "NF"

                if st.button("Submit"):
                    case_id = str(uuid.uuid4())
                    image_path = f"./resources/{case_id}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(image_obj.read())

                    new_case = PublicSubmissions(
                        id=case_id,
                        submitted_by=user_info["name"],
                        face_mesh=json.dumps(face_mesh),
                        location=location,
                        mobile=mobile,
                        email=email,
                        status=status,
                        birth_marks=birth_marks,
                    )
                    db_queries.new_public_case(new_case)
                    st.success("Sighting submitted successfully!")

elif st.session_state.get("authentication_status") == False:
    st.error("Username/password is incorrect")
elif st.session_state.get("authentication_status") == None:
    st.warning("Please enter your username and password")
    st.session_state["login_status"] = False
