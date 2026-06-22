const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const config = require('../config');

async function checkout(req, res, next) {
  try {
    const { usr: userName, eml: userEmail, pwd: password, c_id: courseId, card } = req.body;

    if (!userName || !userEmail || !courseId || !card) {
      return res.status(400).json({ error: 'Bad Request: name, email, course_id, and card are required' });
    }

    const course = await courseModel.getActiveCourseById(courseId);
    if (!course) {
      return res.status(404).json({ error: 'Course not found' });
    }

    const paymentStatus = card.startsWith('4') ? 'PAID' : 'DENIED';
    if (paymentStatus === 'DENIED') {
      return res.status(400).json({ error: 'Payment declined' });
    }

    const user = await userModel.findOrCreateUser(userName, userEmail, password);
    const enrollmentId = await enrollmentModel.createEnrollment(user.id, courseId);
    await paymentModel.createPayment(enrollmentId, course.price, paymentStatus);
    await paymentModel.logAudit(`Checkout course ${courseId} by user ${user.id}`);

    res.status(200).json({ msg: 'Success', enrollment_id: enrollmentId });
  } catch (err) {
    next(err);
  }
}

module.exports = { checkout };
