/**
 * HR Analytics & Automation System
 * Google Apps Script for Automated Alerts
 * 
 * Modul: Late Alert System & Candidate Stagnation Alert
 */

// ==========================================
// CONFIGURATION
// ==========================================
const CONFIG = {
  TARGET_EMAIL: "hr.manager@example.com", // Hardcoded email untuk testing
  LATE_THRESHOLD: 3,                      // Batas maksimal telat per minggu
  STAGNANT_DAYS_THRESHOLD: 5,             // Batas maksimal hari tersendat
  SHEET_ATTENDANCE: "processed_attendance",
  SHEET_RECRUITMENT: "recruitment_pipeline",
  SHEET_ALERTS: "alerts_log"
};

// ==========================================
// 1. MAIN AUTOMATION RUNNER
// ==========================================
/**
 * Fungsi utama (Entry Point) yang akan dieksekusi oleh Trigger
 */
function runHRISAutomation() {
  Logger.log(" Memulai HRIS Automation Pipeline...");
  try {
    // 1. Eksekusi Pengecekan Keterlambatan
    checkLateEmployees();
    
    // 2. Eksekusi Pengecekan Kandidat Mandek
    checkStagnantCandidates();
    
    Logger.log("✅ HRIS Automation Pipeline selesai dieksekusi tanpa error.");
  } catch (error) {
    Logger.log("❌ ERROR pada runHRISAutomation: " + error.message);
    sendEmailAlert("URGENT: HRIS System Error", "Terjadi kesalahan pada sistem automasi HRIS: \n\n" + error.message);
  }
}

// ==========================================
// 2. BUSINESS LOGIC FUNCTIONS
// ==========================================

/**
 * Memeriksa karyawan yang terlambat > 3 kali dalam seminggu
 */
function checkLateEmployees() {
  Logger.log("  -> Menjalankan checkLateEmployees...");
  
  const attendanceData = getProcessedAttendanceData();
  if (attendanceData.length === 0) {
    Logger.log("     Data attendance kosong. Dilewati.");
    return;
  }

  // Agregasi jumlah telat per Karyawan per Minggu
  // Struktur: { "EMP001_2026-W09": { emp_id: "EMP001", total_late: 4, week: "2026-W09" } }
  const lateCounter = {};
  
  attendanceData.forEach(row => {
    // Pastikan membaca nilai string 'TRUE' atau boolean true
    let isLate = (row['late_flag'] === true || row['late_flag'] === 'TRUE' || row['late_flag'] === 'True');
    
    if (isLate) {
      let key = row['employee_id'] + "_" + row['week_number'];
      
      if (!lateCounter[key]) {
        lateCounter[key] = {
          empId: row['employee_id'],
          week: row['week_number'],
          count: 0
        };
      }
      lateCounter[key].count++;
    }
  });

  // Evaluasi threshold dan Trigger Alert
  for (let key in lateCounter) {
    let record = lateCounter[key];
    
    if (record.count > CONFIG.LATE_THRESHOLD) {
      let message = `Employee ${record.empId} has been late more than ${CONFIG.LATE_THRESHOLD} times this week (${record.week}). Total Lates: ${record.count}`;
      
      // Kirim Email
      sendEmailAlert(`🚨 Indiscipline Alert: ${record.empId}`, message);
      
      // Catat ke log
      logAlert("late", record.empId, message);
    }
  }
}

/**
 * Memeriksa kandidat rekrutmen yang tidak bergerak > 5 hari
 */
function checkStagnantCandidates() {
  Logger.log("  -> Menjalankan checkStagnantCandidates...");
  
  // Karena tidak ada fungsi spesifik diminta untuk getRecruitment, kita buat pembaca data langsung
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_RECRUITMENT);
  if (!sheet) throw new Error("Sheet recruitment_pipeline tidak ditemukan!");
  
  const data = getSheetDataAsObjects(sheet);
  const today = new Date();
  
  data.forEach(row => {
    // Hanya periksa kandidat yang masih berstatus 'Active' dan belum di stages akhir
    let validToTrack = (row['status'] === 'Active' || row['status'] === 'Passed') && 
                       (row['stage'] !== 'Hired' && row['stage'] !== 'Rejected');
                       
    if (validToTrack) {
      let stageDate = new Date(row['stage_timestamp']);
      
      // Kalkulasi perbedaan hari (Mili Detik -> Hari)
      let diffTime = Math.abs(today - stageDate);
      let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
      
      if (diffDays > CONFIG.STAGNANT_DAYS_THRESHOLD) {
        let message = `Candidate ${row['candidate_id']} has been in ${row['stage']} for more than ${CONFIG.STAGNANT_DAYS_THRESHOLD} days.`;
        
        sendEmailAlert(`⚠️ Recruitment Bottleneck: ${row['candidate_id']} stuck in ${row['stage']}`, message);
        logAlert("candidate_stuck", row['candidate_id'], message);
      }
    }
  });
}


// ==========================================
// 3. UTILITY & HELPER FUNCTIONS
// ==========================================

/**
 * Mengambil data dari sheet processed_attendance menjadi array of objects
 */
function getProcessedAttendanceData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_ATTENDANCE);
  if (!sheet) {
    throw new Error(`Sheet ${CONFIG.SHEET_ATTENDANCE} tidak ditemukan di Google Sheets ini.`);
  }
  return getSheetDataAsObjects(sheet);
}

/**
 * Helper universal untuk mengambil data Range Google Sheets dan memetakannya sesuai Header
 */
function getSheetDataAsObjects(sheet) {
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  
  if (values.length <= 1) return []; // Hanya header atau kosong
  
  const headers = values[0];
  const rows = values.slice(1);
  
  const objectArray = rows.map(row => {
    let obj = {};
    headers.forEach((header, index) => {
      obj[header] = row[index];
    });
    return obj;
  });
  
  return objectArray;
}

/**
 * Fungsi untuk mencatat aktivitas ke alerts_log
 */
function logAlert(type, referenceId, message) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_ALERTS);
  
  if (!sheet) {
    Logger.log("❌ ERROR: Sheet alerts_log tidak ditemukan. Gagal menyimpan log.");
    return;
  }
  
  // Format [timestamp, type, reference_id, message]
  const timestamp = new Date();
  sheet.appendRow([timestamp, type, referenceId, message]);
  Logger.log(`   [LOGGED] Alert ${type} untuk ${referenceId} berhasil dicatat.`);
}

/**
 * Fungsi pembungkus untuk menembak Email Notifikasi
 */
function sendEmailAlert(subject, body) {
  try {
    GmailApp.sendEmail({
      to: CONFIG.TARGET_EMAIL,
      subject: subject,
      body: body,
      name: "HRIS Automation Bot"
    });
    Logger.log(`   [EMAIL SENT] Subject: ${subject}`);
  } catch (error) {
    Logger.log(`❌ ERROR mengirim email: ${error.message}`);
  }
}

// ==========================================
// 4. TRIGGER SETUP (CRON JOB)
// ==========================================

/**
 * Fungsi untuk setup trigger harian otomatis (Jalankan sekali di awal)
 */
function setupDailyTriggers() {
  // Hapus trigger lama (jika ada) demi mencegah duplikasi eksekusi
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === "runHRISAutomation") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Buat Trigger baru: Setiap hari berjalan pada jam 08:30 (Mendekati jam 8-9 pagi)
  ScriptApp.newTrigger("runHRISAutomation")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .nearMinute(30)
    .create();
    
  Logger.log("✅ Daily Trigger untuk runHRISAutomation berhasil diset pada pukul ~08:30");
}
