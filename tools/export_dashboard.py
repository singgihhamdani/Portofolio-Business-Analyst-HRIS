import pandas as pd
import plotly.express as px
from datetime import datetime
import os

print("\n[1/3] Loading Data for Executive Dashboard...")

# 1. Load Data
employees = pd.read_csv('../data/employee_master.csv')
attendance = pd.read_csv('../data/attendance_log.csv')
recruitment = pd.read_csv('../data/recruitment_pipeline.csv')

# --- DATA PREP ---
attendance = attendance.drop_duplicates()
attendance['date'] = pd.to_datetime(attendance['date'])
attendance['status'] = attendance['status'].fillna('absent')
attendance['overtime_minutes'] = attendance['overtime_minutes'].fillna(0)
attendance['late_flag'] = attendance['status'] == 'late'

employees['join_date'] = pd.to_datetime(employees['join_date'])
recruitment['stage_timestamp'] = pd.to_datetime(recruitment['stage_timestamp'])

attendance = attendance[attendance['employee_id'].isin(employees['employee_id'].unique())]
merged_df = pd.merge(attendance, employees, on='employee_id', how='left')

# --- KPI CALCULATION ---
total_expected_days = len(attendance)
total_present = len(attendance[attendance['status'].isin(['present', 'late'])])
attendance_rate = (total_present / total_expected_days) * 100

total_employees = len(employees)
resigned_employees = len(employees[employees['status'] == 'Resign'])
turnover_rate = (resigned_employees / total_employees) * 100

total_overtime_hours = attendance['overtime_minutes'].sum() / 60
total_normal_hours = total_expected_days * 8
overtime_rate = (total_overtime_hours / total_normal_hours) * 100

applied_dates = recruitment[recruitment['stage'] == 'Applied'][['candidate_id', 'stage_timestamp']]
hired_dates = recruitment[recruitment['stage'] == 'Hired'][['candidate_id', 'stage_timestamp']]
tth_df = pd.merge(hired_dates, applied_dates, on='candidate_id', suffixes=('_hired', '_applied'))
avg_tth = (tth_df['stage_timestamp_hired'] - tth_df['stage_timestamp_applied']).dt.days.mean()

print("[2/3] Generating Corporate Charts...")

# --- CHARTS ---
color_primary = "#0d6efd"     # Blue Corporate
color_secondary = "#6c757d"   # Gray
color_success = "#198754"     # Green
color_danger = "#dc3545"      # Red
color_warning = "#ffc107"     # Yellow
color_info = "#0dcaf0"        # Light Blue
font_corporate = "Inter, sans-serif"

# A. Headcount Overview
headcount = employees.groupby(['department', 'status']).size().reset_index(name='count')
fig0 = px.bar(headcount, x='department', y='count', color='status',
              title='Headcount by Department',
              color_discrete_map={'Active': color_primary, 'Resign': color_danger},
              barmode='group', text_auto=True)
fig0.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# B. Attendance Trend
daily_att = attendance.groupby(['date', 'status']).size().reset_index(name='count')
fig1 = px.line(daily_att, x='date', y='count', color='status', 
               title='Daily Attendance Velocity',
               color_discrete_map={'present': color_success, 'late': color_warning, 'absent': color_danger})
fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# C. Lateness per Dept
late_dept = merged_df[merged_df['late_flag'] == True].groupby('department').size().reset_index(name='total_lates')
fig2 = px.bar(late_dept.sort_values('total_lates'), x='total_lates', y='department', orientation='h',
              title='Lateness Frequency Hotspots', 
              color='total_lates', color_continuous_scale='Blues', text_auto=True)
fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# D. Recruitment Funnel
stage_counts = recruitment.groupby('stage')['candidate_id'].nunique().reindex(
    ['Applied', 'Screening', 'Interview', 'Offering', 'Hired']).reset_index(name='candidates')
fig3 = px.funnel(stage_counts, x='candidates', y='stage', title='Recruitment Drop-Off Pipeline',
                 color_discrete_sequence=[color_primary])
fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# E. Turnover by Dept
resign_dept = employees[employees['status'] == 'Resign'].groupby('department').size().reset_index(name='resigned')
total_dept = employees.groupby('department').size().reset_index(name='total')
turnover_dept = pd.merge(total_dept, resign_dept, on='department', how='left').fillna(0)
turnover_dept['turnover_pct'] = (turnover_dept['resigned'] / turnover_dept['total'] * 100).round(1)

fig4 = px.bar(turnover_dept.sort_values('turnover_pct', ascending=False),
               x='department', y='turnover_pct',
               title='Turnover Rate Benchmark (%)',
               color='turnover_pct', color_continuous_scale='Reds', text_auto='.1f')
fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# F. Overtime Distribution (Cost)
merged_df['daily_ot_hours'] = merged_df['overtime_minutes'] / 60
merged_df['daily_ot_cost'] = (merged_df['base_salary'] / 173) * merged_df['daily_ot_hours']
ot_dept = merged_df.groupby('department')['daily_ot_cost'].sum().reset_index()

fig5 = px.bar(ot_dept.sort_values('daily_ot_cost', ascending=False), 
              x='department', y='daily_ot_cost',
              title='Total Overtime Cost (IDR) per Department',
              color='daily_ot_cost', color_continuous_scale='Oranges', text_auto=',.0f')
fig5.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family=font_corporate)

# Convert all figures to HTML div strings
div_fig0 = fig0.to_html(full_html=False, include_plotlyjs='cdn')
div_fig1 = fig1.to_html(full_html=False, include_plotlyjs=False) 
div_fig2 = fig2.to_html(full_html=False, include_plotlyjs=False)
div_fig3 = fig3.to_html(full_html=False, include_plotlyjs=False)
div_fig4 = fig4.to_html(full_html=False, include_plotlyjs=False)
div_fig5 = fig5.to_html(full_html=False, include_plotlyjs=False)

print("[3/3] Compiling Clean Corporate HTML...")

# Read the HTML template
with open('dashboard_template.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace placeholders with actual data
html_out = template.replace('{date_generated}', datetime.now().strftime('%d %B %Y'))
html_out = html_out.replace('{attendance_rate:.1f}', f"{attendance_rate:.1f}")
html_out = html_out.replace('{turnover_rate:.1f}', f"{turnover_rate:.1f}")
html_out = html_out.replace('{avg_tth:.0f}', f"{avg_tth:.0f}")
html_out = html_out.replace('{overtime_rate:.2f}', f"{overtime_rate:.2f}")

# Replace Charts
html_out = html_out.replace('{div_fig0}', div_fig0)
html_out = html_out.replace('{div_fig1}', div_fig1)
html_out = html_out.replace('{div_fig2}', div_fig2)
html_out = html_out.replace('{div_fig3}', div_fig3)
html_out = html_out.replace('{div_fig4}', div_fig4)
html_out = html_out.replace('{div_fig5}', div_fig5)

# Write final HTML
output_path = '../docs/Executive_Dashboard_RBAC.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f"✅ Clean Corporate Dashboard berhasil diekspor ke: {output_path}")
print("   Sistem RBAC terpenuhi: Director hanya bisa melihat HTML ini tanpa akses ke kernel Jupyter.")
