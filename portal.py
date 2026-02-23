import streamlit as st
import requests
import pandas as pd
from datetime import date

URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Elite University", layout="wide")

# Custom Royal Blue Styling
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #002366 !important; font-weight: bold; }
    .stButton>button { 
        background-color: #002366; color: white; border-radius: 8px; 
        width: 100%; height: 3.5em; font-size: 18px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0047AB; transform: scale(1.02); }
    .css-1offfwp { background-color: #f0f2f6; border-radius: 10px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Programs List
programs = ["BS Computer Science", "BS AI", "BS Software Engineering", "MS Data Science", "MBA"]

menu = st.sidebar.radio("MENU", ["Student Portal", "Admin Dashboard"])

if menu == "Student Portal":
    st.title("🏛️ University Admission Portal")
    
    with st.form("admission_form", clear_on_submit=True):
        st.subheader("1. Profile Information")
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name")
        dob = c2.date_input("Date of Birth", min_value=date(1995, 1, 1))
        
        st.subheader("2. Academic Details")
        prog_choice = st.selectbox("Select Program", programs)
        c3, c4 = st.columns(2)
        ssc = c3.number_input("SSC Marks", 0, 1100)
        hssc = c4.number_input("HSSC Marks", 0, 1100)
        
        st.subheader("3. Document Upload (PDF/JPG)")
        files = st.file_uploader("Upload SSC, HSSC Marksheets & CNIC", accept_multiple_files=True)
        
        if st.form_submit_button("SUBMIT APPLICATION"):
            if name and files:
                # FormData format for files
                data = {"name": name, "dob": str(dob), "program": prog_choice, "ssc": ssc, "hssc": hssc}
                file_payload = [('files', (f.name, f.getvalue(), f.type)) for f in files]
                
                try:
                    r = requests.post(f"{URL}/submit_application", data=data, files=file_payload)
                    st.success(f"Application Received! Your ID: {r.json()['id']}")
                    st.balloons()
                except:
                    st.error("Connection Error: Is the Backend (app.py) running?")

    st.markdown("---")
    st.subheader("💳 Secure Payment")
    pc1, pc2 = st.columns(2)
    p_id = pc1.text_input("Enter Admission ID")
    card = pc2.text_input("Card Number (4242)", type="password")
    if st.button("CONFIRM PAYMENT"):
        r = requests.post(f"{URL}/pay", json={"id": p_id, "card": card})
        st.success("Payment Successful!") if r.status_code == 200 else st.error("Failed")

else:
    st.title("🛡️ Admin Dashboard")
    # Admin login logic (Same as before but inside attractive UI)
    if "auth" not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        with st.form("admin_login"):
            u = st.text_input("Admin Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN"):
                if u == "admin123" and p == "admin@uni":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Wrong Password")
    else:
        st.subheader("📊 Live Merit List")
        r = requests.get(f"{URL}/admin/list")
        df = pd.DataFrame(r.json())
        if not df.empty:
            st.dataframe(df[['admission_id', 'name', 'program', 'merit', 'payment']].style.set_properties(**{'background-color': '#f9f9f9'}))
        if st.button("Logout"): 
            st.session_state.auth = False
            st.rerun()