const { dbGet, dbAll, dbRun } = require('../database');

async function getActiveCourseById(id) {
  return dbGet("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
}

async function getAllCourses() {
  return dbAll("SELECT * FROM courses");
}

module.exports = { getActiveCourseById, getAllCourses };
