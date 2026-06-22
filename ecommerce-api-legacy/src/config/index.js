require('dotenv').config();

module.exports = {
  dbUser: process.env.DB_USER || '',
  dbPass: process.env.DB_PASS || '',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
};
