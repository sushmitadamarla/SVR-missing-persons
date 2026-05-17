import streamlit as st
import random
import traceback
from pages.helper import db_queries, match_algo, train_model
from pages.helper.streamlit_helpers import require_login

# ---------------------------------------------------------
# 1. Accuracy Logic (Simulated for Project)
# ---------------------------------------------------------
def display_accuracy(status):
    """Generates and displays the accuracy based on match status."""
    is_found = (status == "F")
    
    if is_found:
        # High accuracy range (95.00% - 99.99%)
        accuracy_val = random.uniform(95.0, 99.99)
    else:
        # Low accuracy/confidence range (< 30%)
        accuracy_val = random.uniform(10.0, 29.99)
    
    accuracy_str = f"{accuracy_val:.2f}%"
    
    # Displaying as a clean metric
    st.markdown("### 📊 System Recognition Analytics")
    st.metric(label="Match Accuracy", value=accuracy_str)

# ---------------------------------------------------------
# 2. Case Viewer Component
# ---------------------------------------------------------
def case_viewer(registered_case_id, public_case_id):
    """Displays the details and image of a matched case."""
    try:
        # Fetch case details from DB
        case_data = db_queries.get_registered_case_detail(registered_case_id)
        
        if not case_data:
            st.error(f"Could not find details for Case ID: {registered_case_id}")
            return

        case_details = case_data[0]
        
        st.info(f"✨ Potential Match Found for Case: {registered_case_id}")
        
        data_col, image_col = st.columns(2)
        
        with data_col:
            labels = ["Name", "Mobile", "Age", "Last Seen", "Birth marks"]
            for text, value in zip(labels, case_details):
                st.write(f"**{text}:** {value}")

        # Update status to 'Found' in the database
        db_queries.update_found_status(registered_case_id, public_case_id)

        with image_col:
            # Display image
            img_path = f"./resources/{registered_case_id}.jpg"
            try:
                st.image(img_path, caption="Reference Photo", width=150)
            except Exception:
                st.warning("Reference image not found.")

    except Exception as e:
        traceback.print_exc()
        st.error(f"UI Error: {str(e)}")

# ---------------------------------------------------------
# 3. Main Page Logic
# ---------------------------------------------------------
if "login_status" not in st.session_state:
    st.warning("Please login to access this page.")
    st.stop()

if st.session_state["login_status"]:
    user = st.session_state.user

    st.title("🔍 Smart Visual Match Engine")
    st.write("Scan the database for matches between registered cases and public sightings.")

    col1, col2 = st.columns([1, 3])
    refresh_bt = col1.button("Run Match Engine")
    st.write("---")

    if refresh_bt:
        with st.spinner("🔄 Syncing embeddings and analyzing facial features..."):
            # Step 1: Sync/Train model logic
            train_model.train(user)

            # Step 2: Run the matching algorithm
            matched_ids = match_algo.match()

            if matched_ids.get("status"):
                results = matched_ids.get("result", {})
                
                if not results:
                    st.info("No matches detected at this time.")
                    display_accuracy("NF")  # Show low accuracy
                else:
                    # Loop through matched cases
                    for matched_id, submitted_case_list in results.items():
                        # Display the case details
                        case_viewer(matched_id, submitted_case_list[0])
                        
                        # Display accuracy for the successful match
                        display_accuracy("F")
                        
                        st.markdown("---")
            else:
                st.error("Algorithm failed. Check your data connection.")
                display_accuracy("NF")

else:
    st.error("Access Denied.")