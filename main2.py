from datetime import date
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:mysql123@localhost/students_data")
df = pd.read_sql("SELECT * FROM attendance_risk", engine)

today = date.today()
insert_data = []

for _, row in df.iterrows():
    insert_data.append({
        'student_id': row['student_id'],
        'risk_reason': f"Low attendance in {row['low_attendance_subjects']} subjects",
        'risk_level': 'High' if row['low_attendance_subjects'] >= 3 else 'Medium',
        'prediction_date': today
    })

risk_df = pd.DataFrame(insert_data)
risk_df.to_sql('risk_predictions', con=engine, if_exists='append', index=False)
print("✅ Attendance risks saved to risk_predictions.")
