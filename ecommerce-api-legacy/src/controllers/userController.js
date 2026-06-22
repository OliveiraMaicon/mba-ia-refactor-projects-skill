const userModel = require('../models/userModel');

async function deleteUser(req, res, next) {
  try {
    const userId = parseInt(req.params.id);
    const user = await userModel.getUserById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    await userModel.deleteUserById(userId);
    res.json({ message: 'User and associated records deleted successfully' });
  } catch (err) {
    next(err);
  }
}

module.exports = { deleteUser };
