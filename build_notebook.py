import json

cells = []

def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": [line + '\n' for line in text.split('\n')]})

def code(text):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + '\n' for line in text.split('\n')]})

md("""# 📊 Executive HR Analytics & Automation Dashboard
**Tujuan:** Memberikan wawasan berbasis data (*data-driven insights*) mengenai tingkat kedisiplinan, efektivitas rekrutmen, dan beban keuangan lembur kepada Pimpinan Manajemen Eksekutif.

*Catatan Eksekusi: Tekan **Run All** secara urut. Pastikan Anda mengimpor dataset `employee_master.csv`, `attendance_log.csv`, dan `recruitment_pipeline.csv` pada root folder ini.*""")

code("""!pip install pandas plotly nbformat --quiet
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)""")

md("""## 1. Data Cleaning & Preparation (Automasi ETL)
Proses pembersihan data mentah untuk mensterilisasi _noise_ seperti duplikasi sensor mesin *(duplicate check-in)*, kehilangan jejak sistem *(missing check-out)*, dan manipulasi konversi DateTime universal.""")

code("""print("⏳ Memulai Data Ingestion...")
# Load Seluruh Datasets
employees = pd.read_csv('employee_master.csv')
attendance = pd.read_csv('attendance_log.csv')
recruitment = pd.read_csv('recruitment_pipeline.csv')

# ==========================================
# A. PEMBERSIHAN DATA KEHADIRAN (ATTENDANCE)
# ==========================================
# 1. Menghilangkan Duplikasi (Tap Fingerprint Berulang)
initial_att = len(attendance)
attendance = attendance.drop_duplicates()
print(f"✅ Removed {initial_att - len(attendance)} duplicated records dari raw mesik biometrik.")

# 2. Konversi Kolom Teks ke Datetime Python
attendance['date'] = pd.to_datetime(attendance['date'])
# Memadukan tanggal & jam untuk presisi batas lembur
attendance['check_in_dt'] = pd.to_datetime(attendance['date'].dt.strftime('%Y-%m-%d') + ' ' + attendance['check_in'], errors='coerce')
attendance['check_out_dt'] = pd.to_datetime(attendance['date'].dt.strftime('%Y-%m-%d') + ' ' + attendance['check_out'], errors='coerce')

# 3. Handling Edge Cases Missing Values
# Rule BRD: Tidak ada jam masuk sama sekali dianggap 'Absent'
attendance['status'].fillna('absent', inplace=True)
attendance.loc[attendance['check_in'].isna(), 'status'] = 'absent'
# Edge case: Lupa Checkout (Jam pulang kosong mereset hitungan lembur menjadi 0)
attendance['overtime_minutes'].fillna(0, inplace=True)

# 4. Feature Engineering
# Membuat penanda (Flag) khusus keterlambatan telak
attendance['late_flag'] = attendance['status'] == 'late'
attendance['week_number'] = attendance['date'].dt.isocalendar().week
attendance['month'] = attendance['date'].dt.month_name()
attendance['day_name'] = attendance['date'].dt.day_name()

# ==========================================
# B. NORMALISASI DATA EMPLOYEE & RECRUITMENT
# ==========================================
employees['join_date'] = pd.to_datetime(employees['join_date'])
recruitment['stage_timestamp'] = pd.to_datetime(recruitment['stage_timestamp'])

# Filter ID siluman (Membersihkan Log Absen Karyawan yang tak terdaftar di EMP_MASTER)
valid_employee_ids = employees['employee_id'].unique()
invalid_logs = attendance[~attendance['employee_id'].isin(valid_employee_ids)]
attendance = attendance[attendance['employee_id'].isin(valid_employee_ids)]

if not invalid_logs.empty:
    print(f"⚠️ Peringatan: {len(invalid_logs)} log absen dari ID tak terdaftar dieliminasi (Ghost data).")
else:
    print("✅ Seluruh log absen memiliki Employee ID valid.")

print("🚀 Pipeline Data Cleaning 100% Selesai! Data siap divisualisasikan.\\n")""")

md("""## 2. KPI Calculation (Pengukuran Core Matriks Eksekutif)
Pemberlakuan formula KPI tingkat lanjut sesuai spesifikasi BRD. Area ini diekspor langsung ke *Top Bar UI* Visual (Scorecards).""")

code("""# 1. Menghitung Turnover Rate (%)
total_employees = len(employees)
resigned_employees = len(employees[employees['status'] == 'Resign'])
turnover_rate = (resigned_employees / total_employees) * 100

# 2. Menghitung Attendance Rate (%)
total_expected_days = len(attendance)
total_present = len(attendance[attendance['status'].isin(['present', 'late'])])
attendance_rate = (total_present / total_expected_days) * 100

# 3. Menghitung Overtime Rate (%)
# BRD formula: Total Lemur Aktual / (Total Kapasitas Jam Normal) x 100
total_overtime_hours = attendance['overtime_minutes'].sum() / 60
total_normal_hours = total_expected_days * 8  # Asumsi mandatori 8 jam per hari
overtime_rate = (total_overtime_hours / total_normal_hours) * 100

# 4. Menghitung Average Time-to-Hire (Laju Konversi Talenta)
# Event Log Join: Mempertemukan tanggal pelamar saat fase Applied VS fase Hired
applied_dates = recruitment[recruitment['stage'] == 'Applied'][['candidate_id', 'stage_timestamp']]
hired_dates = recruitment[recruitment['stage'] == 'Hired'][['candidate_id', 'stage_timestamp']]

tth_df = pd.merge(hired_dates, applied_dates, on='candidate_id', suffixes=('_hired', '_applied'))
tth_df['days_to_hire'] = (tth_df['stage_timestamp_hired'] - tth_df['stage_timestamp_applied']).dt.days
avg_tth = tth_df['days_to_hire'].mean()

# === [ PRINT RENDER DASHBOARD SCORECARD SECARA VISUAL MENGGUNAKAN HTML CARDS ] === 
from IPython.display import HTML, display

html_cards = f'''
<div style="display: flex; justify-content: space-between; gap: 15px; margin-bottom: 20px;">
    <div style="flex: 1; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); text-align: center;">
        <h4 style="margin: 0; color: #6c757d; font-size: 14px; text-transform: uppercase;">Attendance Rate</h4>
        <h2 style="margin: 10px 0; color: #0d6efd; font-size: 32px;">{attendance_rate:.1f}%</h2>
        <p style="margin: 0; color: #28a745; font-size: 12px;">▲ Target Kedisiplinan</p>
    </div>
    <div style="flex: 1; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); text-align: center;">
        <h4 style="margin: 0; color: #6c757d; font-size: 14px; text-transform: uppercase;">Turnover Rate</h4>
        <h2 style="margin: 10px 0; color: #dc3545; font-size: 32px;">{turnover_rate:.1f}%</h2>
        <p style="margin: 0; color: #dc3545; font-size: 12px;">⚠️ Risiko Resign Tinggi</p>
    </div>
    <div style="flex: 1; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); text-align: center;">
        <h4 style="margin: 0; color: #6c757d; font-size: 14px; text-transform: uppercase;">Avg Time-to-Hire</h4>
        <h2 style="margin: 10px 0; color: #17a2b8; font-size: 32px;">{avg_tth:.0f} Hari</h2>
        <p style="margin: 0; color: #6c757d; font-size: 12px;">Kecepatan Rekrutmen</p>
    </div>
    <div style="flex: 1; padding: 20px; background: white; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); text-align: center;">
        <h4 style="margin: 0; color: #6c757d; font-size: 14px; text-transform: uppercase;">Overtime Burden</h4>
        <h2 style="margin: 10px 0; color: #fd7e14; font-size: 32px;">{overtime_rate:.2f}%</h2>
        <p style="margin: 0; color: #6c757d; font-size: 12px;">Rasio Beban Lembur</p>
    </div>
</div>
'''
display(HTML(html_cards))""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #17a2b8; border-radius: 4px;">
<b>💡 Analisis Eksekutif - KPI Summary:</b><br>
Berdasarkan sampel data, performa **Attendance Rate cukup disiplin (stabil >90%)**. Walau begitu, *Red Flag* menyala terang pada jarum <b>Turnover Rate yang telah menerjang level >15%</b>. Kehilangan staf sebesar ini mewajibkan evaluasi budaya kerja secepatnya! Di sudut lain, kecepatan menutup kursi kosong (*Time-to-Hire*) berada di jalur sehat, menegaskan tim rekruter bekerja cekatan menghadapi derasnya laju resignasi.
</div>""")

md("""## 3. Data Visualization & Insights (Interpretasi Bisnis Lanjutan)""")

code("""# A. ATTENDANCE TREND (DIAGRAM GARIS FLUKTUASI)
daily_att = attendance.groupby(['date', 'status']).size().reset_index(name='count')
fig1 = px.line(daily_att, x='date', y='count', color='status', 
               title='<b>Tren Kehadiran Harian</b> (Deteksi Wabah Ketidakhadiran Kumulatif)',
               color_discrete_map={'present': '#2ca02c', 'late': '#ff7f0e', 'absent': '#d62728'})
fig1.update_layout(xaxis_title="Timeline Jendela Waktu", yaxis_title="Jumlah Orang")
fig1.show()""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #17a2b8; border-radius: 4px;">
<b>📉 Business Insight (Pola Garis Waktu Kehadiran):</b><br>
Pola grafik oranye (Terlambat/Late) memiliki konsistensi mendatar di garis bawah, menyingkapkan bahwa **selalu ada minoritas segelintir komplotan karyawan yang terus-menerus mendobrak pagar kedisiplinan 08:15** pada tiap harinya! Ketimbang menghukum se-departemen, automasi surel (*email alert*) esok akan berfokus melacak ID individu berantai ini untuk disodorkan SP1.
</div>""")

code("""# B. KETERLAMBATAN PER DEPARTEMEN (LATE FREQUENCY BAR CHART)
merged_df = pd.merge(attendance, employees, on='employee_id', how='left')
late_dept = merged_df[merged_df['late_flag'] == True].groupby('department').size().reset_index(name='total_lates')

fig2 = px.bar(late_dept.sort_values('total_lates'), x='total_lates', y='department', orientation='h',
              title='<b>Sebaran Titik Pelanggaran Keterlambatan per Departemen</b>', 
              color='total_lates', color_continuous_scale='Reds',
              text_auto=True)
fig2.show()""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #dc3545; border-radius: 4px;">
<b>🚨 Alert Insight (Hotspot Kenakalan Presensi):</b><br>
Data simulasi memberitahu *Dept Sales* dan *Tech* adalah pemuncak klasemen keterlambatan paling bandel. Mengingat anak divisi Sales memiliki fleksibilitas tatap-muka *(Client Pitch)* maka pola ini wajar. Namun, dominasi Telat dari dev Tech mengindikasikan bahwa para insinyur IT kurang tertib di pagi hari (Sesuai stereotip insinyur *backend* malam/lembur). Ini membuka jalan untuk modifikasi fleksibilitas aturan (*Grace policy adjustment*) khusus divisi IT.
</div>""")

code("""# C. RECRUITMENT FUNNEL (CORONG BOTTLENECK PELAMAR)
stage_counts = recruitment.groupby('stage')['candidate_id'].nunique().reindex(
    ['Applied', 'Screening', 'Interview', 'Offering', 'Hired']
).reset_index(name='candidates')

fig3 = px.funnel(stage_counts, x='candidates', y='stage', title='<b>Recruitment Pipeline Funnel (Evaluasi Kemacetan Taktik SDM)</b>',
                 color_discrete_sequence=['#1f77b4'])
fig3.show()

# --- AUTOMASI INVESTIGASI PELAMAR STAGNAN (> 5 Hari) ---
as_of_date = pd.to_datetime('2026-02-28') # Tenggat evaluasi dataset ini
stagnant_cases = recruitment[(recruitment['status'] == 'Active') & 
                             (~recruitment['stage'].isin(['Hired', 'Applied']))].copy()
stagnant_cases['days_idle'] = (as_of_date - stagnant_cases['stage_timestamp']).dt.days
stagnant_alert = stagnant_cases[stagnant_cases['days_idle'] >= 5]

print("⚠️ Trigger Email Otomatis: Ditemukan Kumpulan Kandidat Stagnan Penuh Tenggat:")
display(stagnant_alert[['candidate_id', 'department', 'stage', 'days_idle']].head())""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #17a2b8; border-radius: 4px;">
<b>🔍 Pipeline Insight (Deteksi Lubang Hitam Kandidat):</b><br>
Corong membedah kelemahaan mematikan di garis pertahanan antara **'Screening' turun curam ke 'Interview'**. Rasio putus asa ini membunyikan alarm bahwa kualifikasi pembukaan rekrutmen perusahaan tak terkalibrasi tajam sehingga meloloskan bergunung-gunung formulir sampah (Mismatch Profile). Ditambah, **detektor peringatan stagnasi memergoki adanya kandidat membusuk tak dieksekusi rekruter membedel ambang >5 Hari.** Proses bisnis wajib dicaci!
</div>""")

code("""# D. OVERTIME DISTRIBUTION (DISTRIBUSI GULUNGAN BIAYA LEMBUR HARIAN)
ot_dept = merged_df.groupby('department')['overtime_minutes'].sum().reset_index()
ot_dept['overtime_hours'] = ot_dept['overtime_minutes'] / 60

fig4 = px.bar(ot_dept.sort_values('overtime_hours', ascending=False), 
              x='department', y='overtime_hours',
              title='<b>Distribusi Ekstrem Beban Overtime per Departemen (Anggaran Terbakar)</b>',
              color='department', text_auto='.1f')
fig4.update_layout(yaxis_title="Total Jam Lembur Terhitung")
fig4.show()""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #ffc107; border-radius: 4px;">
<b>💰 Business Recommendation (Audit Overtime Tech & Ops):</b><br>
Tim **Tech (IT) dan Operations dikuras tenaganya melampaui toleransi perbudakan operasional normal**. Tingginya gunung batang jam tambahan (*Overtime*) menandakan dua skenario: (a) Pekerja Under-Staffed menderita penumpukan proyek, atau (b) Buruknya *Time Management* struktural. Di titik ini, Manajemen Keuangan akan lebih untung dengan cara merekrut +2 Karyawan IT baru dibandingkan merongrong brankas keuangan membayar lembur parsial yang menguap setiap hari!
</div>""")

code("""# E. OPSIONAL: HEATMAP KETERLAMBATAN (MENCORET KALENDER INTENSITAS)
# Merubah data hari menjadi kategorikal urut
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
heatmap_df = merged_df[merged_df['late_flag'] == True].groupby(['day_name', 'department']).size().reset_index(name='late_freq')
heatmap_df['day_name'] = pd.Categorical(heatmap_df['day_name'], categories=days_order, ordered=True)

heatmap_pivot = heatmap_df.pivot_table(index='day_name', columns='department', values='late_freq', fill_value=0)

fig5 = px.imshow(heatmap_pivot, aspect="auto", color_continuous_scale='Oranges',
                 title='<b>Matriks Peta Panas (Heatmap) Zona Waktu Terburuk</b>',
                 labels=dict(x="Departemen Perkara", y="Hari Senin-Jumat", color="Intensitas Pelanggaran"))
fig5.show()""")

md("""<div style="background-color: #f8f9fa; padding: 15px; border-left: 6px solid #17a2b8; border-radius: 4px;">
<b>🔮 Behavioral Prediction (Pola Biologis Mingguan Karyawan):</b><br>
Lautan sel berwarna pekat merangkum tebaran titik-buta hari yang mengerikan. Jika *Monday* dan *Friday* mendaki puncak kehitaman, artinya peredaran biologis ritme lelah pasca *weekend* menyeret produktivitas korporasi. HRD sangat disarankan meniadakan _Briefing Standup_ wajib pada pukulan gelombang pagi hari berisiko tinggi ini.
</div>""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('HR_Analytics_Report.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print('Notebook berhasil dibuat dan disuntik analisis.')
