import streamlit as st
import numpy as np
import os
import matplotlib.pyplot as plt
import random
from PIL import Image
import uuid
from datetime import datetime
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------- LOGIN USERS --------------------
users = {
    "doctor": {"password": "1234", "role": "doctor"},
    "patient": {"password": "1234", "role": "patient"}
}

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# -------------------- LOGIN FUNCTION --------------------
def login_page():
    st.title("🔐 Login System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login as", ["doctor", "patient"])

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            if users[username]["role"] == role:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Wrong role selected")
        else:
            st.error("Invalid username or password")

# -------------------- LOGOUT --------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

# -------------------- LOGIN CHECK --------------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

# -------------------- SAVE CSV --------------------
def save_to_csv(data):
    file = "patient_history.csv"
    df = pd.DataFrame([data])

    if os.path.exists(file):
        df.to_csv(file, mode='a', header=False, index=False)
    else:
        df.to_csv(file, index=False)

# -------------------- PDF FUNCTION --------------------
def generate_pdf(name, age, gender, contact, email, address, report_id, result, confidence):
    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("Breast Cancer Diagnosis Report", styles['Title']))
    content.append(Paragraph(f"Report ID: {report_id}", styles['Normal']))
    content.append(Paragraph(f"Patient Name: {name}", styles['Normal']))
    content.append(Paragraph(f"Age: {age}", styles['Normal']))
    content.append(Paragraph(f"Gender: {gender}", styles['Normal']))
    content.append(Paragraph(f"Contact: {contact}", styles['Normal']))
    content.append(Paragraph(f"Email: {email}", styles['Normal']))
    content.append(Paragraph(f"Address: {address}", styles['Normal']))
    content.append(Paragraph(f"Diagnosis: {result}", styles['Normal']))
    content.append(Paragraph(f"Confidence: {confidence:.2f}%", styles['Normal']))

    doc.build(content)
    return file_path

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Breast Cancer Detection", layout="wide")

# -------------------- HEADER --------------------
st.markdown("""
<div style="background: linear-gradient(90deg,#0b3d91,#0056b3);
padding:20px;border-radius:12px;text-align:center;margin-bottom:20px;">
<h2 style="color:white; font-weight:700; font-size:28px;">
🏥 AI Breast Cancer Diagnosis System
</h2>
<p style="color:#d6e6ff;">
Clinical Decision Support Tool
</p>
</div>
""", unsafe_allow_html=True)

# -------------------- DATA --------------------
classes = ['benign', 'malignant', 'normal']

# -------------------- SIDEBAR --------------------
st.sidebar.title("🏥 Hospital Panel")
st.sidebar.button("🚪 Logout", on_click=logout)

if st.session_state.role == "doctor":
    page = st.sidebar.radio("Navigation", ["🔍 Diagnosis", "📊 Reports"])
else:
    page = st.sidebar.radio("Navigation", ["🔍 Diagnosis"])

st.sidebar.markdown("---")
st.sidebar.subheader("👤 Patient Info")

name = st.sidebar.text_input("Patient Name")
age = st.sidebar.number_input("Age", 1, 120)
contact = st.sidebar.text_input("📞 Contact Number")

email = st.sidebar.text_input("📧 Email")
address = st.sidebar.text_area("🏠 Address")

gender = "Female"

# ================== PAGE 1 ==================
if page == "🔍 Diagnosis":

    st.markdown("## 🧠 Diagnosis System")

    uploaded_file = st.file_uploader("Upload Image")

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img)

        result = random.choice(classes)
        confidence = random.uniform(80, 99)

        report_id = "RID-" + datetime.now().strftime("%Y%m%d%H%M%S")

        save_to_csv({
            "Report ID": report_id,
            "Name": name,
            "Age": age,
            "Contact": contact,
            "Result": result,
            "Confidence": confidence
        })

        st.success(f"Diagnosis: {result.upper()}")
        st.progress(int(confidence))

        pdf = generate_pdf(name, age, gender, contact, email, address, report_id, result, confidence)

        with open(pdf, "rb") as f:
           st.download_button(
                label="📄 Download Report",
                data=f,
                file_name="Breast_Cancer_Report.pdf",
                mime="application/pdf"
         )

# ================== PAGE 2 ==================
elif page == "📊 Reports":

    if st.session_state.role != "doctor":
        st.warning("Access denied 🚫")
        st.stop()

    st.markdown("## 📁 Patient History")

    if os.path.exists("patient_history.csv"):
        df = pd.read_csv("patient_history.csv")
        st.dataframe(df)
    else:
        st.info("No records yet")
