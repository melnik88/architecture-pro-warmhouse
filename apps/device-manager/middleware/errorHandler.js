const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message);
  console.error('Stack:', err.stack);

  let statusCode = 500;
  let message = 'Internal server error';

  if (err.message.includes('not found')) {
    statusCode = 404;
    message = 'Device not found';
  } else if (err.message.includes('validation')) {
    statusCode = 400;
    message = 'Validation error';
  }

  res.status(statusCode).json({
    success: false,
    error: message,
    details: process.env.NODE_ENV === 'development' ? err.message : undefined,
    timestamp: new Date().toISOString()
  });
};

module.exports = {
  errorHandler
};
