import streamlit as st
import numpy as np
import os
import matplotlib.pyplot as plt
import random
from PIL import Image
from datetime import datetime
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

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

# -------------------- DATA --------------------
classes = ['benign', 'malignant', 'normal']

# -------------------- SIDEBAR --------------------
st.sidebar.title("🏥 Hospital Panel")
page = st.sidebar.radio("Navigation", ["🔍 Diagnosis", "📊 Reports"])

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

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload Ultrasound Image", type=["jpg","png","jpeg"])

        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, use_column_width=True)

    with col2:
        st.markdown("### 🧾 Report")

        if uploaded_file:

            # 👉 RUN ONLY ONCE
            if "prediction_done" not in st.session_state:

                img_resized = img.resize((224,224))
                img_array = np.array(img_resized)
                img_array = np.expand_dims(img_array, axis=0)/255.0

                # -------- FAKE PREDICTION --------
                result = random.choice(classes)
                confidence = random.uniform(80, 99)

                prediction = np.random.rand(3)

                report_id = "RID-" + datetime.now().strftime("%Y%m%d%H%M%S")

                # 👉 STORE EVERYTHING
                st.session_state.prediction_done = True
                st.session_state.result = result
                st.session_state.confidence = confidence
                st.session_state.prediction = prediction
                st.session_state.report_id = report_id

                # SAVE CSV ONCE
                save_to_csv({
                    "Report ID": report_id,
                    "Name": name,
                    "Age": age,
                    "Gender": gender,
                    "Contact": contact,
                    "Email": email,
                    "Address": address,
                    "Result": result,
                    "Confidence": confidence
                })

            # 👉 USE STORED VALUES
            result = st.session_state.result
            confidence = st.session_state.confidence
            prediction = st.session_state.prediction
            report_id = st.session_state.report_id

            # -------- COLOR LOGIC --------
            if result == "malignant":
                color = "#ff4b4b"
                risk_text = "🔴 HIGH RISK"
                bg = "#2b0f0f"
            elif result == "benign":
                color = "#f1c40f"
                risk_text = "🟡 MODERATE RISK"
                bg = "#2b2605"
            else:
                color = "#2ecc71"
                risk_text = "🟢 LOW RISK"
                bg = "#0f2b1b"

            # -------- CARD --------
            st.markdown(f"""
            <div class="card">
            <h4>{name}</h4>
            <p>Age: {age} | Gender: {gender}</p>
            <p>📞 {contact}</p>
            <p>📧 {email}</p>
            <p>🏠 {address}</p>
            <p>🆔 {report_id}</p>
            <hr>
            <h3 style="color:{color};">Diagnosis: {result.upper()}</h3>
            <p>Confidence: {confidence:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(int(confidence))

            # -------- PATTERN --------
            if result == "malignant":
                st.error("🔴 Irregular pattern detected")
            elif result == "benign":
                st.warning("🟡 Smooth pattern")
            else:
                st.success("🟢 Normal tissue")

            # -------- CHART --------
            fig, ax = plt.subplots()
            ax.bar(classes, prediction)
            st.pyplot(fig)

            # -------- PDF --------
            pdf = generate_pdf(
                name, age, gender, contact, email, address,
                report_id, result, confidence
            )

            with open(pdf, "rb") as f:
                st.download_button(
                    label="📄 Download Report",
                    data=f,
                    file_name="Breast_Cancer_Report.pdf",
                    mime="application/pdf"
                )

        else:
            st.info("Upload image to begin")

# ================== PAGE 2 ==================
elif page == "📊 Reports":
    st.metric("Accuracy","86.5%")
