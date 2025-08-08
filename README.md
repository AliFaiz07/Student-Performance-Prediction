


🎓 Student Performance Prediction

A data-driven system to identify students at risk of academic underperformance using **Python**, **Machine Learning, and Streamlit.  
It analyzes academic, attendance, and behavioral data to generate risk levels, visualize trends, and collect faculty feedback for improved predictions.

---

📌 Features
- **Data Aggregation** from MySQL (attendance, assignments, exams, faculty feedback)
- **Predictive Analytics** to classify students into High, Medium, and Low risk
- **Interactive Dashboard** built with Streamlit
- **Faculty Feedback Module** to validate and refine predictions
- **Risk Simulation Tool** for “what-if” analysis
- Export risk reports as CSV

---

## 🛠 Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python (Pandas, NumPy, scikit-learn, SQLAlchemy)
- **Database:** MySQL
- **Visualization:** Plotly, Matplotlib, WordCloud
- **Other Tools:** Faker (dummy data), Git & GitHub

---

📂 Project Structure

.
├── dashboard.py               # Streamlit dashboard
├── generate_ml_dataset.py      # Generates ML-ready dataset
├── InsertingDummyData.py       # Inserts sample data into MySQL
├── main.py                     # Attendance risk calculation
├── main2.py                    # Risk prediction from attendance
├── main3.py                    # Risk prediction from exams, assignments, feedback
├── requirements.txt            # Dependencies
└── docs/
    └── Student Performance Prediction Report.docx
