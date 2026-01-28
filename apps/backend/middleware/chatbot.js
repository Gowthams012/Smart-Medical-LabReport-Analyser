/**
 * ChatBot Middleware
 * Validation and rate limiting for chat operations
 */

const ChatBot = require('../Database/Models/ChatBotModels');

/**
 * Validate chat message
 */
const validateMessage = (req, res, next) => {
    const { message, chatId } = req.body;

    // Check message exists and is not empty
    if (!message || typeof message !== 'string') {
        return res.status(400).json({
            success: false,
            message: 'Message is required and must be a string'
        });
    }

    // Check message length
    if (message.trim().length === 0) {
        return res.status(400).json({
            success: false,
            message: 'Message cannot be empty'
        });
    }

    if (message.length > 1000) {
        return res.status(400).json({
            success: false,
            message: 'Message too long (max 1000 characters)'
        });
    }

    // Check chatId exists
    if (!chatId) {
        return res.status(400).json({
            success: false,
            message: 'Chat ID is required'
        });
    }

    next();
};

/**
 * Validate start chat request
 */
const validateStartChat = (req, res, next) => {
    const { reportId } = req.body;

    if (!reportId) {
        return res.status(400).json({
            success: false,
            message: 'Report ID is required'
        });
    }

    next();
};

/**
 * Rate limiting for chat messages
 * Prevent spam/abuse
 */
const chatRateLimit = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const { chatId } = req.body;

        // Find the chat session
        const chatSession = await ChatBot.findOne({
            _id: chatId,
            userID: userId
        });

        if (!chatSession) {
            return res.status(404).json({
                success: false,
                message: 'Chat session not found'
            });
        }

        // Check if last message was sent within last 2 seconds
        if (chatSession.chatHistory.length > 0) {
            const lastMessage = chatSession.chatHistory[chatSession.chatHistory.length - 1];
            const timeSinceLastMessage = Date.now() - new Date(lastMessage.timestamp).getTime();
            
            if (timeSinceLastMessage < 2000) {
                return res.status(429).json({
                    success: false,
                    message: 'Please wait before sending another message'
                });
            }
        }

        next();
    } catch (error) {
        console.error('Rate limit check error:', error);
        next(); // Don't block on rate limit errors
    }
};

/**
 * Check chat ownership
 */
const checkChatOwnership = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const chatId = req.params.chatId || req.body.chatId;

        const chatSession = await ChatBot.findOne({
            _id: chatId,
            userID: userId
        });

        if (!chatSession) {
            return res.status(404).json({
                success: false,
                message: 'Chat session not found or access denied'
            });
        }

        // Attach chat session to request for reuse
        req.chatSession = chatSession;
        next();
    } catch (error) {
        console.error('Chat ownership check error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to verify chat ownership',
            error: error.message
        });
    }
};

module.exports = {
    validateMessage,
    validateStartChat,
    chatRateLimit,
    checkChatOwnership
};