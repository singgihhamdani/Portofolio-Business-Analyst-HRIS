# 🎯 Portfolio Presentation Deck: HR Analytics & Automation System
*(Panduan Slide by Slide untuk PowerPoint / Google Slides)*

**Tips Desain:** Gunakan *template* slide yang bersih (minimalis), dominasi warna putih/abu-abu terang dengan *accent color* biru korporat (melambangkan teknologi/profesionalitas).

---

## Slide 1: Title Slide
*   **Title (Besar):** HR Analytics & Automation System
*   **Subtitle:** Transforming Manual HR Operations into Data-Driven & Automated Ecosystems
*   **Nama Anda:** [Nama Anda]
*   **Role Target:** Business Analyst / Product Manager Candidate
*   **Visual:** Ilustrasi vektor simpel atau logo minimalis yang melambangkan integrasi data & orang (*people*).

---

## Slide 2: Executive Summary
*   **Title Slide:** Executive Summary
*   **Bullet Points:**
    *   **The Project:** Simulasi sistem HRIS ujung-ke-ujung (End-to-End) yang mengubah manajemen data SDM manual menjadi terpusat, terotomatisasi, dan berbasis analitik.
    *   **My Role:** Bertindak sebagai *Product Manager* penuh: mulai dari inisiasi *Business Requirement Document (BRD)*, pemodelan *System Design*, iterasi MVP, hingga eksekusi ETL & Automasi teknis.
    *   **Core Outcomes:** Memangkas waktu pelaporan HR hingga 80%, memberikan visibilitas instan terhadap *Turnover* & Biaya Lembur eksekutif, serta membangun notifikasi indisipliner tanpa intervensi manusia.
*   **Visual:** Boleh teks tebal pada "Core Outcomes".

---

## Slide 3: The Problem (AS-IS)
*   **Title Slide:** The HR Operational Bottlenecks
*   **Layout:** 3 Kotak Berjejer (*Columns*)
    1.  **Scattered Data:** Data absensi, laporan rekrutmen, dan master karyawan berserakan di spreadsheet terpisah. Menghambat proses *Payroll*.
    2.  **Zero Visibility:** Manajemen kesulitan melacak tren "siapa yang sering telat" atau "kenapa biaya lembur departemen IT tiba-tiba membengkak".
    3.  **Silent Pipeline:** Kandidat pelamar sering menggantung >5 hari tanpa *follow-up*, merusak skor *Time-to-Hire*.
*   **Visual:** Icon menyilang (❌) warna merah di tiap kotak.

---

## Slide 4: Proposed Solution & Product Strategy
*   **Title Slide:** The TO-BE Solution: Centralized, Automated, Insightful
*   **Product Thinking Strategy:**
    *   Membangun arsitektur *Cloud-Native Lightweight* menggunakan Google Workspace & Python sebagai fondasi awal sebelum *scaling* ke SQL & BI Tools.
    *   Pendekatan MVP (Minimum Viable Product): Fokus menyelesaikan rasa sakit terbesar (*Late alerts* & *Payroll readiness*).
*   **Visual:** Panah dari kondisi kacau (kiri) menuju ikon "*Gear/Automation*" dan Dashboard terstruktur (kanan).

---

## Slide 5: System Architecture & Data Flow
*   **Title Slide:** Technical Architecture
*   **Flowchart Visual (Gambarkan ulang secara simpel / Masukkan screenshot diagram Mermaid BRD):**
    *   *Data Source* (CSV Fingerprint / Form) ➔ *Storage* (Google Sheets Hub) ➔ *Processing* (ETL Python & GAS) ➔ *Output* (Python Dashboards & Email Alerts).
*   **Key Talking Point:** "Sebagai Business Analyst, saya merancang arsitektur ini agar data terjamin bersih (*Data Integrity*) sebelum diekspor ke sistem Payload Gaji/Payroll pihak ketiga (misal: gaji.id)."

---

## Slide 6: Key Deliverable 1 - Enterprise Documentation
*   **Title Slide:** Solidifying Requirements: The BRD & SDD
*   **Poin Isi:**
    *   Menerjemahkan *Business Need* menjadi *Functional Requirements* yang presisi (Trigger, Logic, Output).
    *   Menetapkan Aturan Bisnis (*Business Rules*) & Rumusan KPI Matematis (Turnover, Attendance, Overtime) untuk meniadakan ambiguitas bagi Developer.
    *   Menyusun Matriks *Role-Based Access Control* (HR Admin vs Manager vs C-Level) guna menjamin sekuriti PII (*Personally Identifiable Information*).
*   **Visual:** Screenshot sekilas (*mockup*) dokumen BRD (*brd_hris_analytics.md*) atau kutipan tabel skema database Anda.

---

## Slide 7: Key Deliverable 2 - Executive Dashboard
*   **Title Slide:** Data-Driven Decision Making (Python Analytics)
*   **Actionable Visual:** *[INSERT SCREENSHOT HTML CARDS SCORECARD DAN PLOTLY CHART]*
*   **Talking Points (Highlight Business Insight):**
    *   *Jangan jelaskan kodenya, jelaskan dampaknya!*
    *   "Saya merancang *Overview Scorecard* agar C-Level bisa melihat *Red Flags* (misal: Turnover menyentuh 16%)."
    *   "Saya menambahkan Funnel Rekrutmen untuk menemukan bahwa *Drop-off* terbesar terjadi di tahap Screening menuju Interview, mengindikasikan perlunya kalibrasi kualifikasi CV."

---

## Slide 8: Key Deliverable 3 - Automated Alerting System
*   **Title Slide:** Proactive Watchdog: Google Apps Script Automation
*   **Poin Isi:**
    *   Membangun *Cron Job Trigger* harian untuk audit kedisiplinan (Jam 08:30 Pagi).
    *   Menyaring pegawai yang telat >3x seminggu untuk memicu *Warning Email* otomatis ke Atasan.
    *   Menyaring pelamar yang mandek/stagnan >5 Hari di satu tahap untuk menagih evaluasi ke *Recruiter*.
*   **Visual:** Screenshot dari hasil keluaran file `alerts_log.csv` (Kasus keterlambatan EMP012 & Kemacetan pelamar CAND045).

---

## Slide 9: Business Impact & Why Hire Me?
*   **Title Slide:** Delivering Business Value & Real Impact
*   **Bullet Points:**
    *   **Cost Efficiency:** Visibilitas terhadap tren *Overtime* langsung memotong klaim lembur yang tidak efisien dari departemen Tech.
    *   **Agility:** Konversi laporan HR yang dulunya butuh *H+3* (3 hari) menjadi *Live Analytics* (*Real-Time*).
    *   **My Edge (Sebagai Kandidat):** 
        "Saya tidak hanya menerjemahkan dokumen (BRD), tetapi juga memiliki ketajaman teknis (*Technical Acumen*) untuk memvalidasi kelayakan arsitektur (*Data Flow, ETL, API Readiness*) dan memastikan peluncuran *(delivery)* sistem yang sukses."

---

## Slide 10: Let's Connect
*   **Title Slide:** Thank You
*   **Isi:** 
    *   "Open for Technical Interview & Deep-Dive Discussions."
    *   [Nomor Telepon] | [Email]
    *   [URL GitHub / Repositori Proyek] | [URL LinkedIn]
*   **Visual:** QR Code menuju GitHub Repository proyek ini yang berisi file README + Notebook.
