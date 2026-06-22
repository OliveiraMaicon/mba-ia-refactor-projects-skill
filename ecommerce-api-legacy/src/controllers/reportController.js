const { dbAll, dbGet } = require('../database');

async function financialReport(req, res, next) {
  try {
    const courses = await dbAll("SELECT * FROM courses");
    const report = [];

    for (const course of courses) {
      const courseData = { course: course.title, revenue: 0, students: [] };
      const enrollments = await dbAll("SELECT * FROM enrollments WHERE course_id = ?", [course.id]);

      for (const enrollment of enrollments) {
        const user = await dbGet("SELECT name, email FROM users WHERE id = ?", [enrollment.user_id]);
        const payment = await dbGet(
          "SELECT amount, status FROM payments WHERE enrollment_id = ?",
          [enrollment.id]
        );

        if (payment && payment.status === 'PAID') {
          courseData.revenue += payment.amount;
        }

        courseData.students.push({
          student: user ? user.name : 'Unknown',
          paid: payment ? payment.amount : 0
        });
      }

      report.push(courseData);
    }

    res.json(report);
  } catch (err) {
    next(err);
  }
}

module.exports = { financialReport };
