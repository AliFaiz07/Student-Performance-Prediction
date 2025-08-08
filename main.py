import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:mysql123@localhost/students_data")

df_students = pd.read_sql("SELECT * FROM students", engine)
df_attendance = pd.read_sql("SELECT * FROM attendance", engine)

low_attendance = df_attendance[df_attendance['attendance_percentage'] < 75]
attendance_risk = (
    low_attendance.groupby('student_id')
    .size()
    .reset_index(name='low_attendance_subjects')
)

risky_students = pd.merge(attendance_risk, df_students, on='student_id', how='left')
risky_students.to_sql('attendance_risk', engine, if_exists='replace', index=False)
print("✅ Attendance risk data saved.")
