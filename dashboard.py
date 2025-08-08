import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
import base64

# ------------------ Database Connection ------------------
engine = create_engine("mysql+mysqlconnector://root:mysql123@localhost/students_data")

# ------------------ Load Tables ------------------
df = pd.read_sql("SELECT * FROM risk_predictions", engine)
feedback_df = pd.read_sql("SELECT * FROM faculty_feedback", engine)
df_students = pd.read_sql("SELECT student_id FROM students", engine)

# Ensure consistent ID types
df['student_id'] = df['student_id'].astype(str)
feedback_df['student_id'] = feedback_df['student_id'].astype(str)
df_students['student_id'] = df_students['student_id'].astype(str)

# Full list of all student IDs
all_student_ids = sorted(df_students['student_id'].astype(int).tolist())
all_student_ids = [str(i) for i in all_student_ids]  # convert back to string if needed


# ------------------ Sidebar Filters ------------------
st.sidebar.title("🔍 Filters")
selected_id = st.sidebar.selectbox("Select Student ID", ["All"] + all_student_ids)

df['prediction_date'] = pd.to_datetime(df['prediction_date'])
date_range = st.sidebar.date_input("Select Date Range", [df['prediction_date'].min(), df['prediction_date'].max()])
filtered_df = df[(df['prediction_date'] >= pd.to_datetime(date_range[0])) & (df['prediction_date'] <= pd.to_datetime(date_range[1]))]

risk_levels = st.sidebar.multiselect("Select Risk Levels", options=filtered_df['risk_level'].unique(), default=filtered_df['risk_level'].unique())
filtered_df = filtered_df[filtered_df['risk_level'].isin(risk_levels)]

categories = {
    "Academic": ["exam", "assignment", "grades"],
    "Behavioral": ["behavior", "discipline"],
    "Attendance": ["absent", "attendance", "missed"],
    "Miscellaneous": []
}
st.sidebar.markdown("### Risk Reason Categories")
selected_category = st.sidebar.selectbox("Select Risk Category", ["All"] + list(categories.keys()))
if selected_category != "All":
    keywords = categories[selected_category]
    mask = filtered_df['risk_reason'].str.contains('|'.join(keywords), case=False, na=False)
    filtered_df = filtered_df[mask]

if selected_id != "All":
    filtered_df = filtered_df[filtered_df['student_id'] == selected_id]

# ------------------ Export CSV ------------------
st.sidebar.markdown("### 📁 Export")
csv = filtered_df.to_csv(index=False, encoding='utf-8')
b64_csv = base64.b64encode(csv.encode()).decode()
st.sidebar.markdown(f'<a href="data:file/csv;base64,{b64_csv}" download="risk_predictions.csv">📥 Download CSV</a>', unsafe_allow_html=True)

# ------------------ Word Cloud ------------------
st.header("🧠 Word Cloud of Risk Reasons")
if not filtered_df.empty:
    risk_reason_text = " ".join(filtered_df['risk_reason'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(risk_reason_text)
    fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
    ax_wc.imshow(wordcloud, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)
else:
    st.warning("No data available to generate a word cloud.")

# ------------------ Risk Trend ------------------
st.header("📈 Risk Trend Over Time")
time_data = filtered_df.groupby(['prediction_date', 'risk_level']).size().reset_index(name='count')
if not time_data.empty:
    fig_trend = px.line(time_data, x='prediction_date', y='count', color='risk_level', title="Risk Level Trends")
    st.plotly_chart(fig_trend)
else:
    st.warning("No data available to plot risk trend.")

# ------------------ Risk Table ------------------
st.header("📋 Student Risk Table")
st.dataframe(filtered_df)

# ------------------ Student Profile Viewer ------------------
st.header("👤 Student Profile Viewer")
profile_id = st.selectbox("Select Student for Profile", all_student_ids, key="profile_select")
profile_data = df[df['student_id'] == profile_id].sort_values(by='prediction_date')

if not profile_data.empty:
    st.subheader(f"Profile for Student ID: {profile_id}")

    st.markdown("**📊 Confidence Score Timeline**")
    fig_score = px.line(profile_data, x='prediction_date', y='confidence_score', title='Confidence Score Over Time')
    st.plotly_chart(fig_score)

    st.markdown("**📈 Risk Level Timeline**")
    fig_risk = px.scatter(profile_data, x='prediction_date', y='risk_level', color='risk_level')
    st.plotly_chart(fig_risk)

    student_feedback = feedback_df[feedback_df['student_id'] == profile_id]
    if not student_feedback.empty:
        st.markdown("**📌 Faculty Feedback Summary**")
        st.dataframe(student_feedback[['feedback_date', 'comments', 'was_false_positive']])
    else:
        st.info("No feedback submitted for this student.")
else:
    st.info("No prediction history found for Student ID: " + profile_id)

# ------------------ Faculty Feedback Input ------------------
st.header("✍️ Faculty Feedback")
with st.form("feedback_form"):
    selected_feedback_id = st.selectbox("Select Student", all_student_ids, key="feedback_select")
    feedback_text = st.text_area("Enter Feedback")
    false_positive = st.checkbox("Mark as False Positive")
    clarity = st.slider("Clarity (1-10)", 1, 10, 5)
    engagement = st.slider("Engagement (1-10)", 1, 10, 5)
    support = st.slider("Support (1-10)", 1, 10, 5)
    submitted = st.form_submit_button("Submit Feedback")
    if submitted:
        feedback_date = datetime.now().strftime("%Y-%m-%d")
        query = text("""
            INSERT INTO faculty_feedback (student_id, feedback_date, was_false_positive, comments, clarity, engagement, support)
            VALUES (:sid, :fdate, :fp, :comm, :clarity, :engage, :support)
        """)
        with engine.begin() as conn:
            conn.execute(query, {
                "sid": selected_feedback_id,
                "fdate": feedback_date,
                "fp": int(false_positive),
                "comm": feedback_text,
                "clarity": clarity,
                "engage": engagement,
                "support": support
            })
        st.success("✅ Feedback submitted successfully.")

# ------------------ Risk Simulation Tool ------------------
st.header("🔮 Risk Simulation Tool")
sim_student = st.selectbox("Choose Student to Simulate", all_student_ids, key="sim_select")
assignment_score = st.slider("Assignment %", 0, 100, 70)
attendance_score = st.slider("Attendance %", 0, 100, 85)
exam_score = st.slider("Exam Score %", 0, 100, 75)

if st.button("Simulate Risk"):
    avg = np.mean([assignment_score, attendance_score, exam_score])
    if avg > 75:
        risk = "Low"
    elif avg > 50:
        risk = "Medium"
    else:
        risk = "High"
    st.info(f"🧮 Predicted Risk Level: **{risk}** based on simulated values.")
