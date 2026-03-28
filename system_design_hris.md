# System Design Document (SDD)
## Proyek: Sistem HR Analytics & Automation

**Konteks Dokumen:** Translasi Dokumen Kebutuhan Bisnis (BRD v2.0) menjadi Arsitektur Sistem Teknis.  
**Target Pembaca:** Tim Pengembang (Software Engineer, Data Engineer), Tech Lead, dan Tim QA.

---

### 1. System Overview
**Tujuan Sistem:**  
Sistem ini bertindak sebagai jembatan (*middleware* dan *analytics layer*) yang mentransformasi data operasional HR yang berserakan menjadi pusat wawasan (*Single Source of Truth*) dan ekosistem notifikasi otomatis. 

**End-to-End Flow:**  
Data mentah absensi (dari mesin biometrik) dan respons rekrutmen (dari portal/Google Forms) diunggah/masuk ke dalam *Cloud Storage*. Skrip *backend* (Google Apps Script) melakukan pembersihan (*ETL pipeline*) secara terjadwal dan memuatnya ke Tabel Master. Dari sini, mesin berhitung mencari anomali untuk memicu *Email Alert* ke supervisor. Di sisi lain, Python mengambil tabel master via API, melakukan kalkulasi *dataframe*, dan menyajikannya menjadi *Live Interative Dashboard* untuk Manajemen.

---

### 2. System Architecture (Detailed)
Arsitektur dirancang menggunakan pendekatan *Cloud-Native Lightweight* dengan 6 layer komponen:

1. **Data Source Layer**
   - *Biometric Fingerprint Log:* File `.csv` yang diekspor mingguan/harian.
   - *Google Forms/Job Portal:* *Webhook* dari pengisian formulir cuti atau pendaftaran rekrutmen.
2. **Data Storage Layer (Lightweight RDBMS)**
   - *Google Sheets:* Berperan sebagai database relasional awan terpusat (limit 10 juta sel) yang menampung *Fact Table* dan *Dimension Table*. Sangat mudah diakses untuk *manual override* oleh HR.
3. **Data Processing Layer (ETL Engine)**
   - *Google Apps Script (GAS):* Menjadi mesin penggerak (*Cron Job*) yang menangani logika *Data Cleaning* dasar (deduplikasi data, konversi zona waktu).
   - *Python (Pandas):* Melakukan transformasi rumit (*Data Wrangling* lanjutan) seperti agregasi total *turnover* dan kalkulasi selisih jam lembur pada memori terdedikasi.
4. **Automation Layer (Alerting System)**
   - *GAS MailApp Trigger:* Menjalankan siklus penjadwalan (*Event Listener*) harian. Mengeksekusi penembakan *Email SMTP* otomatis berdasarkan paramater *Business Rules*.
5. **Analytics Layer**
   - *Python Math Logic:* Menyimpan definisi rumus (*Attendance Rate, Turnover Rate, Time-to-Hire*) dan melakukan grup komputasi kalkulus pada Dataframe.
6. **Presentation Layer (User Interface)**
   - *Streamlit / Dash Framework:* Mem-parsing hasil *Dataframe Analytics* menjadi Dasbor web interaktif berbasis HTML/JS yang bisa diakses Manajemen via *browser*.

---

### 3. Data Flow Diagram (DFD - Detailed)
Proses Ekstrak, Transformasi, dan *Load* (ETL) dipecah menjadi dua aliran modul fungsional:

#### A. Attendance & Overtime Module Flow
- **Input:** Berkas CSV log masuk `[ID, Tgl, JamMasuk, JamKeluar]`.
- **Cleaning:** 
  - Membuang entri ganda (*deduplication*) jika terekam selisih *tap* mesin < 5 menit.
  - Membuang baris tanpa `ID`.
- **Transformation:** 
  - Standardisasi format `DateTime` (ISO 8601).
  - Normalisasi logika Telat: `IF (JamMasuk > 08:15:00) THEN is_Late = True ELSE False`. (Merujuk ketentuan *BR-01*).
  - Hitung durasi kerja kotor: `[JamKeluar - JamMasuk]`.
- **Classification:** 
  - Melabeli *Record* dengan status: "Hadir On-Time", "Hadir Late", "Alfa", "Lembur".
- **Aggregation:** 
  - Menghitung akumulasi jumlah menit lembur yang *valid* per NIK per periode *Payroll* berjalan.
- **Output:** Baris *Fact Table* bersih di `attendance_log` dan *Trigger Alert* memonitor hari kerja beruntun.

#### B. Recruitment Module Flow
- **Input:** *Payload JSON / Form Response* `[Email Kandidat, Posisi Dilamar, Status Tahap]`.
- **Cleaning:** 
  - Normalisasi email menjadi *lowercase* guna mencegah mendaftar posisi ganda.
- **Transformation:** 
  - Komparasi waktu transisi: `Delta_Days = (Current_Date - stage_updated_at)`.
- **Classification:** 
  - Deteksi Stagnansi: `IF Delta_Days >= 5 AND current_stage != 'Rejected/Hired' THEN flag = 'Stagnant'`.
- **Aggregation:** 
  - Kalkulasi *Average Time-to-Hire* berdasarkan rata-rata selisih awal daftar dan teken kontrak per departemen.
- **Output:** Tabel pelacak `recruitment_pipeline` terbarui; Peringatan peringatan *stuck candidate* siap di *layer UI*.

---

### 4. Data Design (Schema Level)
Sistem menggunakan fondasi skema relasional *(Star Schema sederhana)* untuk memastikan integritas antar-entitas.

**1. Tabel `employee_master` (Dimensi)**
- `emp_id` *(Primary Key, String)*: NIK Unik.
- `emp_name` *(String)*: Nama lengkap.
- `dept_id` *(Foreign Key, String)*: Identitas Divisi/Departemen.
- `job_level` *(String)*: Posisi hierarki (Staff, Supervisor, Manager).
- `join_date` *(Date)*: Tanggal resmi bergabung.
- `status` *(Enum: 'Active', 'Resigned', 'Suspended')*.

**2. Tabel `attendance_log` (Fakta)**
- `log_id` *(Primary Key, Auto-Increment String)*: ID Baris transaksi absen.
- `emp_id` *(Foreign Key, String)*: -> Relasi ke `employee_master`.
- `record_date` *(Date)*: Tanggal absensi.
- `check_in` *(Timestamp)*: Waktu Datang.
- `check_out` *(Timestamp)*: Waktu Pulang.
- `status_id` *(Enum: 'Hadir', 'Telat', 'Alfa', 'Cuti', 'Sakit')*.
- `overtime_mins` *(Integer)*: Total menit lembur bersih.
- `is_approved_ot` *(Boolean):* Flag persetujuan lembur dari atasan (*BR-02*).

**3. Tabel `recruitment_pipeline` (Dimensional & Log)**
- `candidate_id` *(Primary Key, String/Email)*: Kunci identitas kandidat unik.
- `candidate_name` *(String)*.
- `applied_role_id` *(Foreign Key)*: Target lowongan kerja.
- `current_stage` *(Enum: 'Sourcing', 'Screening', 'User Interview', 'Offering', 'Hired', 'Rejected')*.
- `stage_updated_at` *(Timestamp)*: Jejak waktu terakhir status tahap berubah.
- `stagnation_flag` *(Boolean)*: True apabila terhenti > 5 Hari.

---

### 5. Process Flow (User-Based Execution)

**1. HR Admin (Input & Export Phase)**
- *Input:* Admin menaruh *file* CSV tarikan mesin absen lokal ke dalam *Shared Folder Sync/Google Drive*. 
- *Proses:* Sistem GAS di latar belakang otomatis membersihkan dan menyusunnya. Bila terdapat *error log* (ada karyawan lupa *tap* pulang), Admin mengklik sel terkait dan mengisi manual waktu kebijaksanaan (*Manual Override Constraint*).
- *Export:* Ketika tanggal penggajian (Tgl 25) tiba, Admin membuka laman Dasbor Python, memilih Bulan berjalan, lalu mengklik tombol **"Export Payroll-Ready CSV"**. 

**2. HR Manager (Monitoring & Insight)**
- *Login:* Melakukan otentikasi portal (Berbasis *Google SSO / Password*).
- *Journey:* Membuka *Tab "Retention & Turnover"*. Melihat grafik Bar bahwa Divisi Sales menduduki posisi puncak karyawan *resign*. HR Manager dapat menerapkan klik silang/filter departemen tersebut untuk mengekskavasi rincian. Memicunya ke arah kebijakan penyegaran bonus insentif bulanan.

**3. Supervisor (Alert & Action)**
- *Journey:* Datang ke kantor pukul 08:35, Supervisor menerima email subjek *"Warning: Indiscipline Pattern Detected"*.
- *Action:* Email membuka daftar 2 karyawan di timnya yang sudah telat/alfa melebihi batas 3 kali seminggu. Tanpa menunggu rapat tahunan, Supervisor memanggil karyawan tersebut di hari yang sama untuk penertiban lisan/SP1.

---

### 6. Dashboard Design (Wireframe & Business Logic Overview)
Dasbor disajikan dengan struktur komponen yang jelas tanpa ambiguitas ruang:

**A. Top Component: KPI Scorecard Cards**
- **Attendance Rate (%)**: Hijau jika >95%, Merah jika <85%. (Menjelaskan disiplin ritme kerja divisi/perusahaan).
- **Time-to-Hire (Days)**: Angka durasi kelincahan rekruiter menarik *Talent*.
- **Turnover Rate (%)**: Rasio jumlah keluar berbanding personil tetap. Acuan sehat retensi.
- **Overtime Budget Rate (%)**: Rasio jam tambahan vs jam normal, membunyikan penunjuk efisiensi staf vs beban kerja lapangan sebenarnya.

**B. Mid-Component: Major Charts**
- **Trending Line Chart (Daily Attendance):** Menunjukkan pasang-surut kehadiran. *Tujuan Bisnis:* Mendeteksi fenomena "Bolos Jumat/Senin" atau kelumpuhan operasional akibat wabah penyakit berantai.
- **Funnel Chart (Recruitment Drop-Out):** Area menyempit dari Tahap Sourcing -> Penandatanganan Kontrak. *Tujuan Bisnis:* Menemukan titik bocor *drop-out* parah (Misal: Kandidat rontok drastis di Evaluasi Teknis User).

**C. Bottom-Component: Deep Dive Analytics**
- **Stacked Bar Chart (Department Headcount Comparison):** *Tujuan Bisnis:* Pembanding realisasi jumlah personil aktif tiap departemen dibandingkan Anggaran *Budget* Headcount (*Under/Over Staffed*).
- **Grid Heatmap (Lateness Frequency by Day):** Area berwarna merah tua pada sel Kalender. *Tujuan Bisnis:* Menyorot "Hari apa" & "Jam Berapa" intensitas macet/telat karyawan paling ekstrem terjadi.

---

### 7. Automation Flow (Google Apps Script Logic)
Logika diimplementasikan secara statis tanpa intervensi *server-side user* biasa:

1. **Daily Ingestion Job (CRON Trigger: Pukul 23:59)**
   - Algoritma melakukan *Fetch* data terbaru dari titik terminal API/folder hari ini.
   - Melakukan eksekusi modul *Data Cleaning* DFD (Bagian 3A) lalu *Array map* menembakkan `Sheet.appendRow()` menuju *Master Tabel*.
2. **Indiscipline Alert Check (CRON Trigger: Pukul 08:30 Hari Kerja)**
   - *Logic Query:* Mencari baris dengan ID karyawan yang berstatus `is_Late = TRUE` ATAU `status_id = 'Alfa'`. Lalu melancarkan hitung mundur rekaman 7 hari terakhir dari ID terkait. Jika bernilai `>= 3`, ambil Alamat Email atasan terdafar.
   - *Output:* Eksekusi `MailApp.sendEmail()` membawakan Templat Rangkuman HTML ke Atasan berisi NIK, Nama, dan detil hari telat.
3. **Candidate Stagnation Alert (Event On-Form-Commit & Daily)**
   - *Logic Query:* Iterasi pada Tabel Rekrutmen. Mengecek entri non-pungkasan (Selain 'Hired' & 'Rejected'). Apabila selisih tanggal kalender kini vs `stage_updated_at` bernilai `> 5 Days`, sel disorot peringatan (*Stagnation Flag* dimatikan True).
   - *Output:* Laporan rekap harian tertunda dikirimkan ke HR Recruitment Admin.

---

### 8. Integration Design
Bagaimana titik-titik layanan berkomunikasi:
- **Storage ⇆ Ingestion (GAS):** Skrip bersemayam di dalam *Container-Bound Script* Lembar Kerja Google Sheets. Skrip membalas fungsi Triggers yang difasilitasi penuh infrastruktur API Google secara bawaan (*native*).
- **Storage ⇆ Analytics (Python Engine):** Aplikasi Dasbor (dibangun di PC/Cloud Server Python) memanfaatkan pustaka *Pandas* dipasangkan ke *gspread* library dengan pasokan Kunci Servis Akun (*Google Service Account JSON Key*). Sinkronisasi ditarik berdasar interval atau klik *Refresh* halaman Dasbor sehingga Python mem-parsial DataFrame ke memori `df.read_csv()`.
- **Dasbor ⇆ External Payroll:** Integrasi bersifat manual setengah-otomatis bertipe *Flat-File Export*. Python meregenerasi Dataframe yang sudah dijumlah menit-lemburnya, lalu menyajikannya menjadi unduhan `format_gaji.csv` untuk kemudian diimpor HR secara eksternal ke situs Web Gaji.id. Memangkas biaya integrasi API mahal di fase awal.

---

### 9. Error Handling & Edge Cases
Penanganan insiden anomali skematis sistem (*Catch/Try block* logic):
- **Duplicate Check-in (Menge-tap mesin 2 kali dalam sedetik):**
  - *Sistem Handle:* Fungsi agregator ETL membuang himpunan `Check_In Timestamp` serupa, selalu menyimpan *timestamp* terkecil (*Earliest/Min function*) sebagai jam kedatangan aktual.
- **Missing Check-out (Karyawan pulang tanpa tap mesin):**
  - *Sistem Handle:* Mengunci durasi *overtime* menjadi 0. Status tercatat *Warning*. Dasbor HR Admin menandai baris dengan warna Kuning pekat untuk dievaluasi intervensi manual dari *override* Admin HR usai mengonfirmasi kepada penyelia bersangkutan.
- **Invalid Employee ID (Ghost Data/ID tak terdaftar Karyawan):**
  - *Sistem Handle:* Selisih pembacaan ditolak oleh *Master Tabel*. Data diletakkan pada lembar penampungan tabel `error_log`. Administrator akan diberikan pemberitahuan rekap masalah setiap Sabtu siang untuk perbaikan sistematis. 
- **Recruitment Data Tak Ter-update Perekrut:**
  - *Sistem Handle:* Otomatisasi Surel peringatan kandidat macet tak berkesudahan akan terus dikirim jika *stagnation_flag* di bawah limit 60 Hari. Jika belum juga dibenarkan sesudah > 60 hari, *Script* mengeksekusi *Force Closed / Hard Rejected* asimilatif dengan keterangan "Kadaluarsa Sistem" membuangnya ke wadah *Talent Pool*.

---

### 10. Security & Access Control (RBAC Implementation)
Dibangun menggunakan pilar keamanan akses (*Principle of Least Privilege*). Perlindungan dilakukan pada gerbang Dasbor Layar (*Login Access*) dan Proteksi lembar Google Sheets Dasar.
- **HR Admin (Operator):**
  - Akses View: *Full Tactical*. Tab Absensi, Tab Operasi. Visibilitas nominal gaji dikunci permanen (*masked*).
  - Akses Edit: Diperkenankan merubah dan melakukan validasi `attendance_log` secara struktural. 
  - Akses Export: *Enabled*. Mampu mengunduh fail mentah siap-payroll `.CSV`.
- **HR Manager:**
  - Akses View: *Full Macro & Micro overview* (Turnover, Performa Rekrutmen). 
  - Akses Edit: Sebatas hak ganti flag pada tombol *Approve* surat Overtime & Cuti Berbayar.
  - Akses Export: Dokumen Grafis Analisis untuk Presentasi Jajaran (.PDF/.PNG).
- **Director / C-Level Executive:**
  - Akses View: Hanya terpusat ke Laman Ringkasan Bisnis Strategis (Finansial vs SDM).
  - Akses Edit: *Locked* sama sekali (Pencegahan penghapusan tidak sengaja mutlak).
  - Akses Export: Tidak memiliki *button export* pada UI nya guna keamanan kebocoran taktik perusahaan.

---

### 11. Scalability & Future Architecture (Skalabilitas 2-3 Tahun)
Guna mengakomodir penambahan drastis jumlah staf mencapai ratusan, fondasi direkayasa dengan *Roadmap* transisi ke depan:
- **Relational SQL Migration:** Pada batas *Limit Constraints* Google Sheets mendekati 5 juta sel (Estimasi tahun ke-3), tabel dimensi dikukuhkan berpindah menuju **AWS RDS PostgreSQL** atau **Supabase**. Mengganti mekanisme GAS murni ke wujud cron job server perantara (Python Celery).
- **Modern BI Tool Pluck-in:** Menurunkan Dasbor Python kustom tatkala skala organisasi meluas, lalu mengkoneksikan pusat database baru dicolok langsung kepada raksasa visualisasi *Business Intelligence* komersil (Tableau / Metabase / PowerBI) lewat tautan *Query SQL Engine* stabil.
- **Machine Learning Integration (Predictive Churn):** Menyertakan *Scikit-Learn Python library* secara otomatis menganalisis variabel historis data (Jumlah sakit, stagnasi gaji, umur relasi) demi meramalkan probabilitas siapa SDM kunci yang berpotensi menderita persentase niatan pengunduran diri tinggi di kuartal berikut.
