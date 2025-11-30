const express = require('express');
const axios = require('axios');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const app = express();
const PORT = process.env.PORT || 8080;

// Service URLs (using Kubernetes DNS)
const QUIZ_SERVICE_URL = process.env.QUIZ_SERVICE_URL || 'http://quiz-service:5000';
const METRICS_SERVICE_URL = process.env.METRICS_SERVICE_URL || 'http://metrics-service:5001';

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'api-gateway',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    dependencies: {
      quizService: QUIZ_SERVICE_URL,
      metricsService: METRICS_SERVICE_URL,
    },
  });
});

// Root endpoint
app.get('/api', (req, res) => {
  res.json({
    name: 'Word Quiz API Gateway',
    version: '1.0.0',
    endpoints: {
      health: 'GET /api/health',
      quiz: {
        getQuestion: 'GET /api/quiz/question',
        submitAnswer: 'POST /api/quiz/answer',
        getWords: 'GET /api/quiz/words',
      },
      metrics: {
        getStats: 'GET /api/metrics/stats',
        recordMetric: 'POST /api/metrics/record',
      },
    },
  });
});

// ============================================
// Quiz Service Routes
// ============================================

// Get a new quiz question
app.get('/api/quiz/question', async (req, res) => {
  try {
    console.log('Fetching question from quiz service...');
    const response = await axios.get(`${QUIZ_SERVICE_URL}/quiz/generate`, {
      timeout: 5000,
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching question:', error.message);
    res.status(500).json({
      error: 'Failed to fetch question',
      message: error.message,
      service: 'quiz-service',
    });
  }
});

// Submit answer and validate
app.post('/api/quiz/answer', async (req, res) => {
  try {
    const answerData = req.body;
    console.log('Validating answer:', answerData);

    // Validate with quiz service
    const quizResponse = await axios.post(
      `${QUIZ_SERVICE_URL}/quiz/validate`,
      {
        answer: answerData.answer,
        selectedOption: answerData.selectedOption,
      },
      { timeout: 5000 }
    );

    // Record metrics in background (don't wait)
    recordMetrics(answerData).catch(err => 
      console.error('Failed to record metrics:', err.message)
    );

    res.json({
      ...quizResponse.data,
      recorded: true,
    });
  } catch (error) {
    console.error('Error validating answer:', error.message);
    res.status(500).json({
      error: 'Failed to validate answer',
      message: error.message,
    });
  }
});

// Get word bank information
app.get('/api/quiz/words', async (req, res) => {
  try {
    const response = await axios.get(`${QUIZ_SERVICE_URL}/quiz/words`, {
      timeout: 5000,
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching words:', error.message);
    res.status(500).json({
      error: 'Failed to fetch words',
      message: error.message,
    });
  }
});

// ============================================
// Metrics Service Routes
// ============================================

// Get statistics
app.get('/api/metrics/stats', async (req, res) => {
  try {
    console.log('Fetching statistics from metrics service...');
    const response = await axios.get(`${METRICS_SERVICE_URL}/metrics/stats`, {
      timeout: 5000,
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching stats:', error.message);
    res.status(500).json({
      error: 'Failed to fetch statistics',
      message: error.message,
      service: 'metrics-service',
    });
  }
});

// Record metric manually
app.post('/api/metrics/record', async (req, res) => {
  try {
    const metricData = req.body;
    const response = await axios.post(
      `${METRICS_SERVICE_URL}/metrics/record`,
      metricData,
      { timeout: 5000 }
    );
    res.json(response.data);
  } catch (error) {
    console.error('Error recording metric:', error.message);
    res.status(500).json({
      error: 'Failed to record metric',
      message: error.message,
    });
  }
});

// ============================================
// Helper Functions
// ============================================

async function recordMetrics(answerData) {
  try {
    await axios.post(
      `${METRICS_SERVICE_URL}/metrics/record`,
      answerData,
      { timeout: 3000 }
    );
    console.log('Metrics recorded successfully');
  } catch (error) {
    throw new Error(`Metrics recording failed: ${error.message}`);
  }
}

// ============================================
// Error Handling
// ============================================

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`,
    availableRoutes: [
      '/api/health',
      '/api/quiz/question',
      '/api/quiz/answer',
      '/api/metrics/stats',
    ],
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
  });
});

// ============================================
// Start Server
// ============================================

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 API Gateway running on port ${PORT}`);
  console.log(`📡 Quiz Service: ${QUIZ_SERVICE_URL}`);
  console.log(`📊 Metrics Service: ${METRICS_SERVICE_URL}`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});
