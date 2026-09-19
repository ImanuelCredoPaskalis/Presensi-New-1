/**
 * ============================================================
 *  Google Apps Script — Presensi Lab Micro Teaching FisMat
 * ============================================================
 *  Deploy sebagai Web App (Execute as: Me, Who has access: Anyone).
 *  Tempel kode ini di Extensions > Apps Script pada Google Spreadsheet.
 *
 *  Spreadsheet harus punya 4 tab:
 *    • Master_Mahasiswa
 *    • Presensi_Harian
 *    • Log_Aktivitas
 *    • Pengaturan
 *
 *  Aksi yang didukung (via query param ?action=...):
 *    ping              – health-check
 *    upsertMaster      – insert/update baris di Master_Mahasiswa
 *    deleteMaster      – hapus baris di Master_Mahasiswa
 *    savePresensi      – insert/update baris di Presensi_Harian
 *    appendLog         – tambah baris di Log_Aktivitas
 *    getPresensi       – ambil semua baris Presensi_Harian
 * ============================================================
 */

// ────────────────────────────────────────────
//  Entry Point  (POST)
// ────────────────────────────────────────────
function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents || "{}");
    var action = (e.parameter && e.parameter.action) || "";

    switch (action) {
      case "ping":
        return jsonResponse({ ok: true, message: "pong", timestamp: new Date().toISOString() });

      case "upsertMaster":
        return handleUpsertMaster(body);

      case "deleteMaster":
        return handleDeleteMaster(body);

      case "savePresensi":
        return handleSavePresensi(body);

      case "appendLog":
        return handleAppendLog(body);

      case "getPresensi":
        return handleGetPresensi(body);

      default:
        return jsonResponse({ ok: false, error: "Unknown action: " + action });
    }
  } catch (err) {
    return jsonResponse({ ok: false, error: err.message || String(err) });
  }
}

// ────────────────────────────────────────────
//  Helper: JSON response
// ────────────────────────────────────────────
function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ────────────────────────────────────────────
//  Helper: dapatkan sheet berdasarkan nama
// ────────────────────────────────────────────
function getSheet_(name) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    throw new Error("Sheet '" + name + "' tidak ditemukan.");
  }
  return sheet;
}

// ────────────────────────────────────────────
//  Helper: ambil header (baris pertama) → array
// ────────────────────────────────────────────
function getHeaders_(sheet) {
  var lastCol = sheet.getLastColumn();
  if (lastCol === 0) return [];
  return sheet.getRange(1, 1, 1, lastCol).getValues()[0];
}

// ────────────────────────────────────────────
//  Helper: cari baris berdasarkan key_field = key_value
//  Mengembalikan nomor baris (1-based) atau -1.
// ────────────────────────────────────────────
function findRowByField_(sheet, headers, keyField, keyValue) {
  var colIdx = headers.indexOf(keyField);
  if (colIdx === -1) return -1;

  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return -1; // hanya header

  var values = sheet.getRange(2, colIdx + 1, lastRow - 1, 1).getValues();
  for (var i = 0; i < values.length; i++) {
    if (String(values[i][0]).toLowerCase() === String(keyValue).toLowerCase()) {
      return i + 2; // baris ke-(i+2) di spreadsheet
    }
  }
  return -1;
}

// ────────────────────────────────────────────
//  Helper: cari baris berdasarkan beberapa key_field
// ────────────────────────────────────────────
function findRowByMultipleFields_(sheet, headers, keyFields, keyValues) {
  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) return -1;

  var colIndices = keyFields.map(function (f) { return headers.indexOf(f); });
  if (colIndices.indexOf(-1) !== -1) return -1;

  for (var r = 2; r <= lastRow; r++) {
    var rowVals = sheet.getRange(r, 1, 1, headers.length).getValues()[0];
    var match = true;
    for (var k = 0; k < keyFields.length; k++) {
      if (String(rowVals[colIndices[k]]).toLowerCase() !== String(keyValues[k]).toLowerCase()) {
        match = false;
        break;
      }
    }
    if (match) return r;
  }
  return -1;
}

// ────────────────────────────────────────────
//  Helper: tulis baris berdasarkan header & row object
// ────────────────────────────────────────────
function writeRow_(sheet, headers, rowObj, rowNum) {
  var data = headers.map(function (h) {
    return rowObj[h] !== undefined ? rowObj[h] : "";
  });
  sheet.getRange(rowNum, 1, 1, headers.length).setValues([data]);
}

// ────────────────────────────────────────────
//  Helper: tambah baris baru
// ────────────────────────────────────────────
function appendRow_(sheet, headers, rowObj) {
  var data = headers.map(function (h) {
    return rowObj[h] !== undefined ? rowObj[h] : "";
  });
  sheet.appendRow(data);
}

// ────────────────────────────────────────────
//  Aksi: ping (sudah ditangani di doPost)
// ────────────────────────────────────────────

// ────────────────────────────────────────────
//  Aksi: upsertMaster
// ────────────────────────────────────────────
function handleUpsertMaster(body) {
  var sheet = getSheet_(body.sheet || "Master_Mahasiswa");
  var headers = getHeaders_(sheet);
  var row = body.row || {};
  var keyField = body.key_field || "Nama_Mahasiswa";
  var keyValue = body.key_value || row[keyField] || "";
  var replaceKey = body.replace_key || false;

  var existingRow = findRowByField_(sheet, headers, keyField, keyValue);

  if (existingRow > 0) {
    // Update
    if (replaceKey) {
      // Jika key berganti, cari dulu baris berdasarkan key lama (sudah ketemu)
      // Tulis data baru
      writeRow_(sheet, headers, row, existingRow);
    } else {
      writeRow_(sheet, headers, row, existingRow);
    }
    return jsonResponse({ ok: true, message: "Row updated", row: existingRow });
  } else {
    // Insert
    appendRow_(sheet, headers, row);
    return jsonResponse({ ok: true, message: "Row inserted" });
  }
}

// ────────────────────────────────────────────
//  Aksi: deleteMaster
// ────────────────────────────────────────────
function handleDeleteMaster(body) {
  var sheet = getSheet_(body.sheet || "Master_Mahasiswa");
  var headers = getHeaders_(sheet);
  var keyField = body.key_field || "Nama_Mahasiswa";
  var keyValue = body.key_value || "";

  var rowNum = findRowByField_(sheet, headers, keyField, keyValue);
  if (rowNum > 0) {
    sheet.deleteRow(rowNum);
    return jsonResponse({ ok: true, message: "Row deleted", row: rowNum });
  } else {
    return jsonResponse({ ok: false, error: "Row not found for " + keyField + "=" + keyValue });
  }
}

// ────────────────────────────────────────────
//  Aksi: savePresensi (upsert berdasarkan key_fields)
// ────────────────────────────────────────────
function handleSavePresensi(body) {
  var sheet = getSheet_(body.sheet || "Presensi_Harian");
  var headers = getHeaders_(sheet);
  var row = body.row || {};
  var keyFields = body.key_fields || ["Nama_Mahasiswa", "Tanggal"];
  var keyValues = keyFields.map(function (f) { return row[f] || ""; });

  var existingRow = findRowByMultipleFields_(sheet, headers, keyFields, keyValues);

  if (existingRow > 0) {
    writeRow_(sheet, headers, row, existingRow);
    return jsonResponse({ ok: true, message: "Presensi row updated", row: existingRow });
  } else {
    appendRow_(sheet, headers, row);
    return jsonResponse({ ok: true, message: "Presensi row inserted" });
  }
}

// ────────────────────────────────────────────
//  Aksi: appendLog (selalu append, tidak update)
// ────────────────────────────────────────────
function handleAppendLog(body) {
  var sheet = getSheet_(body.sheet || "Log_Aktivitas");
  var headers = getHeaders_(sheet);
  var row = body.row || {};

  appendRow_(sheet, headers, row);
  return jsonResponse({ ok: true, message: "Log appended" });
}

// ────────────────────────────────────────────
//  Aksi: getPresensi (kembalikan semua baris)
// ────────────────────────────────────────────
function handleGetPresensi(body) {
  var sheet = getSheet_(body.sheet || "Presensi_Harian");
  var headers = getHeaders_(sheet);
  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();

  if (lastRow <= 1) {
    return jsonResponse({ ok: true, rows: [] });
  }

  var values = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  var rows = values.map(function (r) {
    var obj = {};
    for (var i = 0; i < headers.length; i++) {
      obj[headers[i]] = r[i] !== undefined ? String(r[i]) : "";
    }
    return obj;
  });

  return jsonResponse({ ok: true, rows: rows });
}

// ────────────────────────────────────────────
//  Optional: GET handler (untuk testing)
// ────────────────────────────────────────────
function doGet(e) {
  var action = (e.parameter && e.parameter.action) || "";
  if (action === "ping") {
    return jsonResponse({ ok: true, message: "pong (GET)", timestamp: new Date().toISOString() });
  }
  return jsonResponse({ ok: true, message: "Presensi Lab GAS Web App is running." });
}
