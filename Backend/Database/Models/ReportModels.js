const mongoose = require('mongoose');

const reportSchema = new mongoose.Schema({
    userID: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: [true, 'User ID is required']
    },
    patientName: {
        type: String,
        trim: true
        // Not required - will be auto-detected by VaultAgent
    },
    reportType: {
        type: String,
        required: [true, 'Report type is required'],
        enum: ['Blood Test', 'Sugar', 'Lipid Profile', 'Complete Blood Count', 'Other'],
        trim: true
    },
    extractedData: {
        type: Object,
        default: {}
    },
    summary: {
        type: String,
        trim: true
    },
    recommendations: {
        type: String, // Store markdown/text recommendations
        trim: true
    },
    riskLevel: {
        type: String,
        enum: ['Normal', 'Medium', 'High', 'Unknown'],
        default: 'Unknown'
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true,
    collection: 'report'
});

// Index for faster queries
reportSchema.index({ userID: 1, createdAt: -1 });

module.exports = mongoose.model('Report', reportSchema);
