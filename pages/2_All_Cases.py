import streamlit as st
import os
from pages.helper import db_queries
from pages.helper.streamlit_helpers import require_login

def case_viewer(case):
    case = list(case)
    case_id = case.pop(0)
    matched_with_id = case.pop(-1)
    matched_with_details = None

    try:
        matched_with_id = matched_with_id.replace("{", "").replace("}", "")
    except Exception:
        matched_with_id = None

    if matched_with_id:
        matched_with_details = db_queries.get_public_case_detail(matched_with_id)

    data_col, image_col, matched_with_col = st.columns(3)
    for text, value in zip(["Name", "Age", "Status", "Last Seen", "Phone"], case[:5]):
        value = "Found" if value == "F" else "Not Found" if value == "NF" else value
        data_col.write(f"{text}: {value}")

        # Display embedding availability
    embedding_check = db_queries.get_embedding_for_case(case_id)
    if embedding_check:
        data_col.write("Face embedding: Available")
    else:
        data_col.write("Face embedding: Missing")


    # Show image (handle missing file gracefully)
    image_path = f"./resources/{case_id}.jpg"
    if os.path.exists(image_path):
        image_col.image(image_path, width=120, use_container_width=False)
    else:
        image_col.warning("Image not found")

    if matched_with_details:
        matched_with_col.write(f"Location: {matched_with_details[0][0]}")
        matched_with_col.write(f"Submitted By: {matched_with_details[0][1]}")
        matched_with_col.write(f"Mobile: {matched_with_details[0][2]}")
        matched_with_col.write(f"Birth Marks: {matched_with_details[0][3]}")
    st.write("---")

    # Delete button with confirmation
    delete_key = f"del_reg_{case_id}"
    confirm_key = f"confirm_del_{case_id}"

    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    def confirm_deletion():
        st.session_state[confirm_key] = True

    st.button("Delete Case", key=delete_key, on_click=confirm_deletion)

    if st.session_state[confirm_key]:
        st.warning(f"Are you sure you want to delete case {case_id}?")

        yes_key = f"yes_del_{case_id}"
        cancel_key = f"cancel_del_{case_id}"

        if st.button("Yes, Delete", key=yes_key):
            db_queries.delete_registered_case(case_id)
            image_path = f"./resources/{case_id}.jpg"
            if os.path.exists(image_path):
                os.remove(image_path)
            st.success("Case deleted!")
            st.session_state[confirm_key] = False
            st.rerun()

        if st.button("Cancel", key=cancel_key):
            st.session_state[confirm_key] = False



def public_case_viewer(case: list) -> None:
    case = list(case)
    case_id = str(case.pop(0))
    data_col, image_col, _ = st.columns(3)
    for text, value in zip(
        ["Status", "Location", "Mobile", "Birth Marks", "Submitted on", "Submitted by"], case
    ):
        if text == "Status":
            value = "Found" if value == "F" else "Not Found"
        data_col.write(f"{text}: {value}")

    image_path = f"./resources/{case_id}.jpg"
    if os.path.exists(image_path):
        image_col.image(image_path, width=120, use_container_width=False)
    else:
        image_col.warning("Image not found")

    st.write("---")

    # Delete button with confirmation
    delete_key = f"del_pub_{case_id}"
    if st.button("Delete Public Case", key=delete_key):
        if st.confirm(f"Are you sure you want to delete public case {case_id}?"):
            db_queries.delete_public_case(case_id)
            if os.path.exists(image_path):
                os.remove(image_path)
            st.success("Public case deleted!")
            st.experimental_rerun()

if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    user = st.session_state.user

    st.title("View Submitted Cases")

    status_col, date_col = st.columns(2)
    status = status_col.selectbox(
        "Filter", options=["All", "Not Found", "Found", "Public Cases"]
    )
    date = date_col.date_input("Date")

    if status == "Public Cases":
        cases_data = db_queries.fetch_public_cases(False, status)
        st.write("\n\n")
        st.write("---")
        for case in cases_data:
            public_case_viewer(case)

    else:
        cases_data = db_queries.fetch_registered_cases(user, status)
        st.write("\n\n")
        st.write("---")
        for case in cases_data:
            case_viewer(case)

else:
    st.write("You don't have access to this page")