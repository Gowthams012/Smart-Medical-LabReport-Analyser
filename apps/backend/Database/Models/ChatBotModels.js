const mongoose = require('mongoose');

const chatHistorySchema = new mongoose.Schema({
    role: {
        type: String,
        required: true,
        enum: ['user', 'assistant']
    },
    message: {
        type: String,
        required: true,
        trim: true
    },
    timestamp: {
        type: Date,
        default: Date.now
    }
}, { _id: false });

const chatBotSchema = new mongoose.Schema({
    userID: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: [true, 'User ID is required']
    },
    relatedReportID: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Report',
        default: null
    },
    chatHistory: [chatHistorySchema],
    createdAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Index for faster queries
chatBotSchema.index({ userID: 1, createdAt: -1 });

module.exports = mongoose.model('ChatBot', chatBotSchema);
