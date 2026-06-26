// Example environment configuration for AutoAds

module.exports = {
  // Server Configuration
  development: {
    port: 3000,
    sessionSecret: 'dev-secret-change-in-production',
    env: 'development'
  },

  production: {
    port: process.env.PORT || 8080,
    sessionSecret: process.env.SESSION_SECRET || 'production-secret-key',
    env: 'production'
  }
};

// Usage in server.js:
// const config = require('./config.js');
// const PORT = config.development.port;
