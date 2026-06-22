const { dbGet, dbRun } = require('../database');
const bcrypt = require('bcrypt');

const SALT_ROUNDS = 10;

async function findOrCreateUser(name, email, password) {
  let user = await dbGet("SELECT id, name, email FROM users WHERE email = ?", [email]);
  if (!user) {
    const hashedPassword = await bcrypt.hash(password || 'default123', SALT_ROUNDS);
    const result = await dbRun(
      "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
      [name, email, hashedPassword]
    );
    user = { id: result.lastID, name, email };
  }
  return user;
}

async function getUserById(id) {
  return dbGet("SELECT id, name, email FROM users WHERE id = ?", [id]);
}

async function deleteUserById(id) {
  await dbRun("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
  await dbRun("DELETE FROM enrollments WHERE user_id = ?", [id]);
  await dbRun("DELETE FROM users WHERE id = ?", [id]);
}

module.exports = { findOrCreateUser, getUserById, deleteUserById };
