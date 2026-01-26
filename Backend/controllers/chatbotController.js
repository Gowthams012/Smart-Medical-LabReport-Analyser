/**
 * ChatBot Controller
 * Handles medical chatbot conversations with context from patient reports
 */

const ChatBot = require('../Database/Models/ChatBotModels');
const Report = require('../Database/Models/ReportModels');
const { spawn } = require('child_process');
const path = require('path');

class ChatBotController {
    constructor() {
        this.projectRoot = path.join(__dirname, '../..');
        this.pythonCmd = 'python';
    }

    /**
     * Start new chat session or continue existing one
     * POST /api/chat/start
     */
    async startChat(req, res) {
        try {
            const { reportId } = req.body;
            const userId = req.user.id;

            // Validate report exists and belongs to user
            const report = await Report.findOne({ _id: reportId, userID: userId });
            if (!report) {
                return res.status(404).json({
                    success: false,
                    message: 'Report not found or access denied'
                });
            }

            // Check if chat session already exists for this report
            let chatSession = await ChatBot.findOne({
                userID: userId,
                relatedReportID: reportId
            });

            if (!chatSession) {
                // Create new chat session
                chatSession = await ChatBot.create({
                    userID: userId,
                    relatedReportID: reportId,
                    chatHistory: []
                });
            }

            res.status(200).json({
                success: true,
                message: 'Chat session ready',
                data: {
                    chatId: chatSession._id,
                    reportId: report._id,
                    patientName: report.patientName,
                    chatHistory: chatSession.chatHistory,
                    reportSummary: report.summary
                }
            });
        } catch (error) {
            console.error('❌ Start chat error:', error);
            res.status(500).json({
                success: false,
                message: 'Failed to start chat session',
                error: error.message
            });
        }
    }

    /**
     * Send message to chatbot
     * POST /api/chat/message
     */
    async sendMessage(req, res) {
        try {
            const { chatId, message } = req.body;
            const userId = req.user.id;

            // Validate input
            if (!message || message.trim().length === 0) {
                return res.status(400).json({
                    success: false,
                    message: 'Message cannot be empty'
                });
            }

            // Find chat session
            const chatSession = await ChatBot.findOne({
                _id: chatId,
                userID: userId
            }).populate('relatedReportID');

            if (!chatSession) {
                return res.status(404).json({
                    success: false,
                    message: 'Chat session not found'
                });
            }

            const report = chatSession.relatedReportID;

            // Validate report has extractedData
            if (!report.extractedData || !report.extractedData.tests || report.extractedData.tests.length === 0) {
                return res.status(400).json({
                    success: false,
                    message: 'Report does not contain valid lab test data. Please process the report first.'
                });
            }

            console.log(`📊 Report has ${report.extractedData.tests.length} tests`);

            // Add user message to history
            chatSession.chatHistory.push({
                role: 'user',
                message: message.trim(),
                timestamp: new Date()
            });

            // Call Python chatbot with report data and chat history
            const botResponse = await this._callChatBot(
                report.extractedData,
                chatSession.chatHistory,
                message
            );

            // Add bot response to history
            chatSession.chatHistory.push({
                role: 'assistant',
                message: botResponse,
                timestamp: new Date()
            });

            // Keep only last 20 messages (10 exchanges)
            if (chatSession.chatHistory.length > 20) {
                chatSession.chatHistory = chatSession.chatHistory.slice(-20);
            }

            await chatSession.save();

            res.status(200).json({
                success: true,
                data: {
                    message: botResponse,
                    chatHistory: chatSession.chatHistory
                }
            });
        } catch (error) {
            console.error('❌ Send message error:', error);
            res.status(500).json({
                success: false,
                message: 'Failed to process message',
                error: error.message
            });
        }
    }

    /**
     * Get chat history
     * GET /api/chat/history/:chatId
     */
    async getChatHistory(req, res) {
        try {
            const { chatId } = req.params;
            const userId = req.user.id;

            const chatSession = await ChatBot.findOne({
                _id: chatId,
                userID: userId
            }).populate('relatedReportID', 'patientName reportType summary');

            if (!chatSession) {
                return res.status(404).json({
                    success: false,
                    message: 'Chat session not found'
                });
            }

            res.status(200).json({
                success: true,
                data: {
                    chatId: chatSession._id,
                    report: chatSession.relatedReportID,
                    chatHistory: chatSession.chatHistory,
                    createdAt: chatSession.createdAt
                }
            });
        } catch (error) {
            console.error('❌ Get history error:', error);
            res.status(500).json({
                success: false,
                message: 'Failed to retrieve chat history',
                error: error.message
            });
        }
    }

    /**
     * Get all chat sessions for user
     * GET /api/chat/sessions
     */
    async getChatSessions(req, res) {
        try {
            const userId = req.user.id;

            const sessions = await ChatBot.find({ userID: userId })
                .populate('relatedReportID', 'patientName reportType createdAt')
                .sort({ updatedAt: -1 })
                .limit(50);

            res.status(200).json({
                success: true,
                count: sessions.length,
                data: sessions.map(session => ({
                    chatId: session._id,
                    report: session.relatedReportID,
                    lastMessage: session.chatHistory.length > 0 
                        ? session.chatHistory[session.chatHistory.length - 1]
                        : null,
                    messageCount: session.chatHistory.length,
                    updatedAt: session.updatedAt
                }))
            });
        } catch (error) {
            console.error('❌ Get sessions error:', error);
            res.status(500).json({
                success: false,
                message: 'Failed to retrieve chat sessions',
                error: error.message
            });
        }
    }

    /**
     * Delete chat session
     * DELETE /api/chat/session/:chatId
     */
    async deleteChat(req, res) {
        try {
            const { chatId } = req.params;
            const userId = req.user.id;

            const result = await ChatBot.findOneAndDelete({
                _id: chatId,
                userID: userId
            });

            if (!result) {
                return res.status(404).json({
                    success: false,
                    message: 'Chat session not found'
                });
            }

            res.status(200).json({
                success: true,
                message: 'Chat session deleted successfully'
            });
        } catch (error) {
            console.error('❌ Delete chat error:', error);
            res.status(500).json({
                success: false,
                message: 'Failed to delete chat session',
                error: error.message
            });
        }
    }

    /**
     * Call Python ChatBot with report data and conversation history
     */
    async _callChatBot(reportData, chatHistory, userMessage) {
        return new Promise((resolve, reject) => {
            // Prepare data to send via stdin (avoids JSON escaping issues)
            const inputData = JSON.stringify({
                reportData,
                chatHistory,
                userMessage
            });

            const code = `
import sys
import os
import json
import tempfile

# Change to project root
os.chdir('${this.projectRoot.replace(/\\/g, '/')}')
sys.path.insert(0, '${this.projectRoot.replace(/\\/g, '/')}/ChatBotAgent')

try:
    from ChatBot import UniversalLabChatbot
    
    # Read data from stdin
    input_json = sys.stdin.read()
    data = json.loads(input_json)
    
    report_data = data['reportData']
    chat_history = data['chatHistory']
    user_message = data['userMessage']
    
    # Debug info
    print(f"DEBUG: Loaded {len(report_data.get('tests', []))} tests", file=sys.stderr)
    
    # Write report data to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
        json.dump(report_data, temp_file)
        temp_file_path = temp_file.name
    
    print(f"DEBUG: Temp file: {temp_file_path}", file=sys.stderr)
    
    # Initialize chatbot
    bot = UniversalLabChatbot(temp_file_path)
    
    # Restore chat history (format: ["User: message", "Bot: response"])
    for msg in chat_history:
        if msg['role'] == 'user':
            bot.chat_history.append(f"User: {msg['message']}")
        elif msg['role'] == 'assistant':
            bot.chat_history.append(f"Bot: {msg['message']}")
    
    print(f"DEBUG: Restored {len(bot.chat_history)} messages", file=sys.stderr)
    
    # Get response
    response = bot.chat(user_message)
    
    # Clean up
    try:
        os.unlink(temp_file_path)
    except:
        pass
    
    print(f"BOT_RESPONSE:{response}")
    
except Exception as e:
    import traceback
    print(f"ERROR:{traceback.format_exc()}")
`;

            const python = spawn(this.pythonCmd, ['-c', code], {
                cwd: this.projectRoot,
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    PYTHONIOENCODING: 'utf-8',
                    GEMINI_API_KEY: process.env.GEMINI_API_KEY || process.env.GOOGLE_GEMINI_API_KEY
                }
            });

            // Send data via stdin
            python.stdin.write(inputData);
            python.stdin.end();

            let output = '';
            let errorOutput = '';

            python.stdout.on('data', (data) => {
                output += data.toString();
            });

            python.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            python.on('close', (exitCode) => {
                // Log full output for debugging
                console.log('🔍 Python Exit Code:', exitCode);
                if (errorOutput) {
                    // Show stderr (includes model switching logs)
                    const stderrLines = errorOutput.split('\n').slice(0, 15); // First 15 lines
                    console.log('📋 Python logs:');
                    stderrLines.forEach(line => {
                        if (line.trim()) console.log('   ', line);
                    });
                }

                if (exitCode !== 0) {
                    return reject(new Error(`ChatBot failed (exit ${exitCode}): ${errorOutput || 'Unknown error'}`));
                }

                // Parse output
                if (output.includes('ERROR:')) {
                    const error = output.split('ERROR:')[1].trim();
                    console.error('❌ Python error:', error.substring(0, 500));
                    return reject(new Error(error));
                }

                if (output.includes('BOT_RESPONSE:')) {
                    // Get everything after BOT_RESPONSE: (including multi-line responses)
                    const response = output.split('BOT_RESPONSE:')[1].trim();
                    console.log('✅ ChatBot response:', response.length, 'chars');
                    return resolve(response);
                }

                console.error('❌ No BOT_RESPONSE marker found in output');
                console.error('Output preview:', output.substring(0, 500));
                reject(new Error('No response from ChatBot'));
            });
        });
    }
}

module.exports = new ChatBotController();