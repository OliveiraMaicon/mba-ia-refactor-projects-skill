const sqlite3 = require('sqlite3').verbose();

let db;

function initDatabase() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(':memory:', (err) => {
      if (err) return reject(err);
    });

    db.serialize(() => {
      db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        pass TEXT
      )`);
      db.run(`CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price REAL,
        active INTEGER
      )`);
      db.run(`CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER
      )`);
      db.run(`CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER,
        amount REAL,
        status TEXT
      )`);
      db.run(`CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`);

      db.get("SELECT COUNT(*) as count FROM users", [], (err, row) => {
        if (row.count === 0) {
          db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            ['Leonan', 'leonan@fullcycle.com.br', '$2b$10$placeholderhash']);
          db.run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
            ['Clean Architecture', 997.00, 1]);
          db.run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
            ['Docker', 497.00, 1]);
          db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
          db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [1, 997.00, 'PAID']);
        }
        resolve(db);
      });
    });
  });
}

function getDb() {
  if (!db) throw new Error('Database not initialized. Call initDatabase() first.');
  return db;
}

function dbGet(sql, params = []) {
  return new Promise((resolve, reject) => {
    getDb().get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function dbAll(sql, params = []) {
  return new Promise((resolve, reject) => {
    getDb().all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

function dbRun(sql, params = []) {
  return new Promise((resolve, reject) => {
    getDb().run(sql, params, function(err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

module.exports = { initDatabase, getDb, dbGet, dbAll, dbRun };
