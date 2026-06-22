const { dbRun } = require('../database');

async function createPayment(enrollmentId, amount, status) {
  const result = await dbRun(
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [enrollmentId, amount, status]
  );
  return result.lastID;
}

async function logAudit(action) {
  await dbRun(
    "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
    [action]
  );
}

module.exports = { createPayment, logAudit };
