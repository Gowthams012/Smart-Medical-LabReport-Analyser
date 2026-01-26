/**
 * Extraction Controller - PDF Upload & Processing
 * ================================================
 * Handles file upload and orchestrates Python agents
 * 
 * Routes:
 * POST /api/extraction/upload - Upload PDF and process through all agents
 * GET  /api/extraction/reports/:id - Get specific report details
 * GET  /api/extraction/reports - Get all user reports
 */

const Report = require('../Database/Models/ReportModels');
const Vault = require('../Database/Models/VaultModels');
const agentService = require('../services/agentService');
const path = require('path');

/**
 * Upload PDF and process through complete pipeline
 * POST /api/extraction/upload
 * 
 * Body: multipart/form-data with 'pdfFile' field
 * Auth: Required (JWT)
 * 
 * Pipeline:
 * 1. Upload PDF → save to user folder
 * 2. VaultAgent → identify patient
 * 3. ExtractionAgent → extract medical data
 * 4. SummaryAgent + RecommendationAgent → generate insights
 * 5. Save to MongoDB → Report collection
 * 6. Update user's Vault
 */
exports.uploadReport = async (req, res) => {
    try {
        // Check if file was uploaded
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'No PDF file uploaded'
            });
        }

        const userId = req.user.id;
        const pdfPath = req.file.path;
        const fileName = req.file.originalname;

        console.log(`\n📥 Processing report for user: ${userId}`);
        console.log(`   File: ${fileName}`);
        console.log(`   Path: ${pdfPath}\n`);

        // Process through complete pipeline
        const result = await agentService.processComplete(pdfPath);

        // Determine risk level from extracted data
        const riskLevel = determineRiskLevel(result.extractedData);

        // Create Report in MongoDB
        const report = await Report.create({
            userID: userId,
            patientName: result.patientName,
            reportType: result.extractedData.reportType || 'Blood Test',
            extractedData: result.extractedData,
            summary: result.summary,
            recommendations: result.recommendations,
            riskLevel: riskLevel
        });

        // Update user's Vault
        await updateUserVault(userId, {
            fileName: fileName,
            fileType: 'application/pdf',
            fileSize: req.file.size,
            fileURL: pdfPath,
            reportId: report._id,
            patientName: result.patientName,
            status: 'processed'
        });

        console.log(`✅ Report saved to database: ${report._id}\n`);

        res.status(201).json({
            success: true,
            message: 'Report processed successfully',
            data: {
                reportId: report._id,
                patientName: result.patientName,
                testCount: result.testCount,
                riskLevel: riskLevel,
                isNewPatient: result.isNewPatient,
                totalReports: result.totalReports,
                summary: result.summary,
                recommendations: result.recommendations
            }
        });

    } catch (error) {
        console.error('❌ Upload error:', error.message);
        res.status(500).json({
            success: false,
            message: 'Failed to process report',
            error: error.message
        });
    }
};

/**
 * Get all reports for authenticated user
 * GET /api/extraction/reports
 */
exports.getMyReports = async (req, res) => {
    try {
        const userId = req.user.id;
        
        const reports = await Report.find({ userID: userId })
            .select('-extractedData') // Exclude large extracted data
            .sort({ createdAt: -1 });

        res.json({
            success: true,
            count: reports.length,
            data: reports
        });
    } catch (error) {
        console.error('Error fetching reports:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch reports',
            error: error.message
        });
    }
};

/**
 * Get specific report by ID
 * GET /api/extraction/reports/:id
 */
exports.getReportById = async (req, res) => {
    try {
        const reportId = req.params.id;
        const userId = req.user.id;

        const report = await Report.findOne({
            _id: reportId,
            userID: userId
        });

        if (!report) {
            return res.status(404).json({
                success: false,
                message: 'Report not found'
            });
        }

        res.json({
            success: true,
            data: report
        });
    } catch (error) {
        console.error('Error fetching report:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch report',
            error: error.message
        });
    }
};

/**
 * Delete report by ID
 * DELETE /api/extraction/reports/:id
 */
exports.deleteReport = async (req, res) => {
    try {
        const reportId = req.params.id;
        const userId = req.user.id;

        const report = await Report.findOneAndDelete({
            _id: reportId,
            userID: userId
        });

        if (!report) {
            return res.status(404).json({
                success: false,
                message: 'Report not found'
            });
        }

        res.json({
            success: true,
            message: 'Report deleted successfully'
        });
    } catch (error) {
        console.error('Error deleting report:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to delete report',
            error: error.message
        });
    }
};

/**
 * Helper: Determine risk level from extracted data
 */
function determineRiskLevel(extractedData) {
    // Simple heuristic: check for out-of-range values
    let outOfRangeCount = 0;
    let totalTests = 0;

    if (extractedData.tests && Array.isArray(extractedData.tests)) {
        totalTests = extractedData.tests.length;
        
        extractedData.tests.forEach(test => {
            if (test.flag || test.status === 'High' || test.status === 'Low') {
                outOfRangeCount++;
            }
        });
    }

    if (totalTests === 0) return 'Unknown';
    
    const percentage = (outOfRangeCount / totalTests) * 100;
    
    if (percentage > 30) return 'High';
    if (percentage > 15) return 'Medium';
    return 'Normal';
}

/**
 * Helper: Update user's vault with new file
 */
async function updateUserVault(userId, fileData) {
    try {
        let vault = await Vault.findOne({ userID: userId });

        if (!vault) {
            vault = await Vault.create({
                userID: userId,
                files: [fileData]
            });
        } else {
            vault.files.push(fileData);
            await vault.save();
        }

        return vault;
    } catch (error) {
        console.error('Error updating vault:', error);
        throw error;
    }
}

module.exports = exports;
