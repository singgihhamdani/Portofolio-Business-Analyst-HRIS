import csv
import random
from datetime import datetime, timedelta

random.seed(42)

departments = ['Sales', 'HR', 'Tech', 'Finance', 'Operations']
job_titles = {
    'Sales': ['Sales Exec', 'Account Mgr', 'VP Sales'],
    'HR': ['HR Admin', 'Recruitment Spec', 'HR Mgr'],
    'Tech': ['Data Analyst', 'Backend Dev', 'Frontend Dev', 'Tech Lead'],
    'Finance': ['Accountant', 'Finance Analyst', 'CFO'],
    'Operations': ['Ops Staff', 'Logistic Coord', 'Ops Manager']
}

# 1. EMPLOYEE MASTER
employees = []
# 42 active, 8 resign = 50 employees
statuses = ['Active']*42 + ['Resign']*8
random.shuffle(statuses)

for i in range(1, 51):
    emp_id = f"EMP{i:03d}"
    dept = random.choice(departments)
    title = random.choice(job_titles[dept])
    join_year = random.randint(2019, 2025)
    join_month = random.randint(1, 12)
    join_day = random.randint(1, 28)
    join_date = f"{join_year}-{join_month:02d}-{join_day:02d}"
    status = statuses[i-1]
    name_suffix = chr(65 + (i % 26))
    name = f"{title.split()[0]} {name_suffix}."
    
    employees.append({
        'employee_id': emp_id,
        'name': f"Pegawai {dept} {i}",
        'department': dept,
        'job_title': title,
        'join_date': join_date,
        'status': status
    })

with open('employee_master.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['employee_id', 'name', 'department', 'job_title', 'join_date', 'status'])
    writer.writeheader()
    writer.writerows(employees)

# 2. ATTENDANCE LOG (2 months: Jan-Feb 2026) -> ~40 working days * 50 emp = 2000 rows
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 2, 28)

attendance_data = []

current_date = start_date
while current_date <= end_date:
    if current_date.weekday() < 5:  # Mon-Fri
        for emp in employees:
            if emp['status'] == 'Resign' and current_date > datetime(2026, 1, 31):
                continue
                
            # ABSENT Logic (3% absent chance uniformly)
            if random.random() < 0.03:
                attendance_data.append({
                    'employee_id': emp['employee_id'],
                    'date': current_date.strftime('%Y-%m-%d'),
                    'check_in': '',
                    'check_out': '',
                    'status': 'absent',
                    'overtime_minutes': 0
                })
                continue
                
            base_in = datetime(current_date.year, current_date.month, current_date.day, 8, 0, 0)
            base_out = datetime(current_date.year, current_date.month, current_date.day, 17, 0, 0)
            
            # LATE Logic
            lateliness_offset = 0
            # EMP012 is chronically late >3x a week
            if emp['employee_id'] == 'EMP012':
                lateliness_offset = random.randint(16, 120) if random.random() < 0.8 else random.randint(-15, 10)
            # Sales Dept notoriously late
            elif emp['department'] == 'Sales' and random.random() < 0.35:
                lateliness_offset = random.randint(16, 90)
            else:
                lateliness_offset = random.randint(-25, 10)
                
            actual_in = base_in + timedelta(minutes=lateliness_offset)
            is_late = actual_in > base_in + timedelta(minutes=15)
            
            # OVERTIME Logic
            overtime = 0
            # Tech Dept has high overtime trend
            if emp['department'] == 'Tech' and random.random() < 0.4:
                overtime = random.randint(60, 240) # 1 to 4 hours
            elif random.random() < 0.1:
                overtime = random.randint(30, 120)
                
            out_offset = overtime + random.randint(0, 10)
            actual_out = base_out + timedelta(minutes=out_offset)
            
            # Missing Check-out Error Edge Case (1% chance)
            str_out = actual_out.strftime('%H:%M:%S')
            if random.random() < 0.01:
                str_out = ""
                overtime = 0
                
            att_stat = 'late' if is_late else 'present'
            
            record = {
                'employee_id': emp['employee_id'],
                'date': current_date.strftime('%Y-%m-%d'),
                'check_in': actual_in.strftime('%H:%M:%S'),
                'check_out': str_out,
                'status': att_stat,
                'overtime_minutes': overtime
            }
            attendance_data.append(record)
            
            # Duplicate Error Edge Case (0.5% chance)
            if random.random() < 0.005:
                attendance_data.append(record)

    current_date += timedelta(days=1)

with open('attendance_log.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['employee_id', 'date', 'check_in', 'check_out', 'status', 'overtime_minutes'])
    writer.writeheader()
    writer.writerows(attendance_data)

# 3. RECRUITMENT PIPELINE
# Generate an event log representing funnel stages.
recruitment_data = []
stages = ['Applied', 'Screening', 'Interview', 'Offering', 'Hired']
target_date = datetime(2026, 2, 28)

for i in range(1, 181): # 180 candidates
    cand_id = f"CAN{i:03d}"
    dept = random.choice(departments)
    pos = random.choice(job_titles[dept])
    
    # Start of stage flow
    base_date = target_date - timedelta(days=random.randint(15, 75))
    
    # Random drop-off fate!
    fate = random.random()
    if fate < 0.4: max_stage = 0
    elif fate < 0.6: max_stage = 1
    elif fate < 0.75: max_stage = 2
    elif fate < 0.85: max_stage = 3
    else: max_stage = 4
    
    for s_idx in range(max_stage + 1):
        stage_name = stages[s_idx]
        
        # Is this the candidate's last stage?
        if s_idx == max_stage:
            if stage_name == 'Hired':
                status = 'Hired'
            else:
                # Some are strictly rejected, some are still hovering/active
                status = random.choice(['Active', 'Rejected'])
                
                # Stagnation Edge Case (>5 days without moving)
                if status == 'Active':
                    base_date = target_date - timedelta(days=random.randint(6, 14))
        else:
            status = 'Passed'
            
        recruitment_data.append({
            'candidate_id': cand_id,
            'position': pos,
            'department': dept,
            'stage': stage_name,
            'stage_timestamp': base_date.strftime('%Y-%m-%d'),
            'status': status
        })
        
        # Increment days for next stage
        base_date += timedelta(days=random.randint(1, 4))
        
with open('recruitment_pipeline.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['candidate_id', 'position', 'department', 'stage', 'stage_timestamp', 'status'])
    writer.writeheader()
    writer.writerows(recruitment_data)
