import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql123",
    database="students_data"
)

attendance_query = """
SELECT student_id, AVG(attendance_percentage) AS avg_attendance
FROM attendance GROUP BY student_id;
"""
df_attendance = pd.read_sql(attendance_query, conn)

assign_query = """
SELECT student_id, subject, AVG(score) AS avg_score
FROM assignments GROUP BY student_id, subject;
"""
df_assignments = pd.read_sql(assign_query, conn)
df_assignments_pivot = df_assignments.pivot(index='student_id', columns='subject', values='avg_score').reset_index()

df_features = pd.merge(df_attendance, df_assignments_pivot, on="student_id", how="left")
df_features.to_csv("student_ml_dataset.csv", index=False)
print("✅ Dataset saved.")
