const mongoose = require('mongoose');

const fileSchema = new mongoose.Schema({
    fileName: {
        type: String,
        required: [true, 'File name is required'],
        trim: true
    },
    uploadDate: {
        type: Date,
        default: Date.now
    },
    fileType: {
        type: String,
        required: [true, 'File type is required'],
        lowercase: true
    },
    fileSize: {
        type: Number,
        required: [true, 'File size is required']
    },
    fileURL: {
        type: String,
        required: [true, 'File URL is required'],
        trim: true
    },
    vaultPath: {
        type: String,
        trim: true
    },
    status: {
        type: String,
        enum: ['uploaded', 'processed', 'failed'],
        default: 'uploaded'
    },
    reportId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Report'
    },
    patientName: {
        type: String,
        trim: true
    }
}, { _id: true });

const vaultSchema = new mongoose.Schema({
    userID: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: [true, 'User ID is required'],
        unique: true  // unique already creates an index, no need for vaultSchema.index()
    },
    files: [fileSchema]
}, {
    timestamps: true
});

module.exports = mongoose.model('Vault', vaultSchema);
