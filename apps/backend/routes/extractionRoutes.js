/**
 * Extraction Routes - PDF Upload & Report Management
 * ===================================================
 * All routes require authentication
 */

const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const upload = require('../middleware/upload');
const extractionController = require('../controllers/extractionController');

// POST /api/extraction/upload - Upload and process PDF
router.post('/upload', auth, upload.single('pdfFile'), extractionController.uploadReport);

// GET /api/extraction/reports - Get all user reports
router.get('/reports', auth, extractionController.getMyReports);

// GET /api/extraction/reports/:id - Get specific report
router.get('/reports/:id', auth, extractionController.getReportById);

// DELETE /api/extraction/reports/:id - Delete report
router.delete('/reports/:id', auth, extractionController.deleteReport);

module.exports = router;
