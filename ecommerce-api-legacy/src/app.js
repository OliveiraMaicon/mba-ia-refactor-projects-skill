const express = require('express');
const { initDatabase } = require('./database');
const config = require('./config');
const errorHandler = require('./middlewares/errorHandler');

const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

async function start() {
  await initDatabase();

  const app = express();
  app.use(express.json());

  app.use('/api', checkoutRoutes);
  app.use('/api/admin', reportRoutes);
  app.use('/api/users', userRoutes);

  app.use(errorHandler);

  app.listen(config.port, () => {
    console.log(`LMS API running on port ${config.port}`);
  });
}

start().catch(console.error);
