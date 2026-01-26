/**
 * ChatBot Routes
 * API endpoints for medical chatbot interactions
 */

const express = require('express');
const router = express.Router();
const chatbotController = require('../controllers/chatbotController');
const auth = require('../middleware/auth');
const {
    validateMessage,
    validateStartChat,
    chatRateLimit
} = require('../middleware/chatbot');

// All routes require authentication
router.use(auth);

/**
 * @route   POST /api/chat/start
 * @desc    Start new chat session or get existing one for a report
 * @access  Private
 * @body    { reportId: string }
 */
router.post('/start', validateStartChat, chatbotController.startChat.bind(chatbotController));

/**
 * @route   POST /api/chat/message
 * @desc    Send message to chatbot
 * @access  Private
 * @body    { chatId: string, message: string }
 */
router.post('/message', validateMessage, chatRateLimit, chatbotController.sendMessage.bind(chatbotController));

/**
 * @route   GET /api/chat/history/:chatId
 * @desc    Get chat history for a session
 * @access  Private
 */
router.get('/history/:chatId', chatbotController.getChatHistory.bind(chatbotController));

/**
 * @route   GET /api/chat/sessions
 * @desc    Get all chat sessions for user
 * @access  Private
 */
router.get('/sessions', chatbotController.getChatSessions.bind(chatbotController));

/**
 * @route   DELETE /api/chat/session/:chatId
 * @desc    Delete chat session
 * @access  Private
 */
router.delete('/session/:chatId', chatbotController.deleteChat.bind(chatbotController));

module.exports = router;