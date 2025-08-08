from datetime import date
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("mysql+pymysql://root:mysql123@localhost/students_data")
df_exams = pd.read_sql("SELECT * FROM exams", engine)
df_assignments = pd.read_sql("SELECT * FROM assignments", engine)
df_feedback = pd.read_sql("SELECT * FROM faculty_feedback", engine)

today = date.today()
risk_entries = []

# Exam Risk
exam_scores = df_exams.groupby('student_id').apply(
    lambda x: x['marks_obtained'].sum() / x['max_marks'].sum()
).reset_index(name='exam_score')
at_risk_exam = exam_scores[exam_scores['exam_score'] < 0.4]

for _, row in at_risk_exam.iterrows():
    risk_entries.append({
        'student_id': row['student_id'],
        'risk_reason': f"Low exam performance: {round(row['exam_score']*100, 2)}%",
        'risk_level': 'High' if row['exam_score'] < 0.3 else 'Medium',
        'prediction_date': today
    })

# Assignment Submission Risk
assignments = df_assignments.groupby('student_id').agg(
    total_submissions=('submitted', 'count'),
    on_time_submissions=('submitted', 'sum')
).reset_index()

assignments['submission_rate'] = assignments['on_time_submissions'] / assignments['total_submissions']
at_risk_assignments = assignments[assignments['submission_rate'] < 0.6]

for _, row in at_risk_assignments.iterrows():
    risk_entries.append({
        'student_id': row['student_id'],
        'risk_reason': f"Low assignment submission rate: {round(row['submission_rate']*100, 2)}%",
        'risk_level': 'Medium',
        'prediction_date': today
    })

# Feedback Risk
feedback_counts = df_feedback.groupby('student_id')['was_false_positive'].sum().reset_index(name='false_positives')
at_risk_feedback = feedback_counts[feedback_counts['false_positives'] >= 2]

for _, row in at_risk_feedback.iterrows():
    risk_entries.append({
        'student_id': row['student_id'],
        'risk_reason': f"Multiple negative feedbacks ({row['false_positives']})",
        'risk_level': 'Medium',
        'prediction_date': today
    })

# Save to DB
if risk_entries:
    pd.DataFrame(risk_entries).to_sql('risk_predictions', con=engine, if_exists='append', index=False)
    print("✅ Combined risk analysis saved.")
else:
    print("✅ No new combined risks.")
