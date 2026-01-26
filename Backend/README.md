# Backend API Server

Medical Report Analysis System - RESTful API

## 📁 Project Structure

```
Backend/
├── config/
│   └── .env                 # Environment configuration
├── controllers/             # Business logic
│   ├── authController.js    # User authentication
│   ├── chatbotController.js # Medical chatbot operations
│   └── extractionController.js # PDF extraction & processing
├── Database/
│   └── Models/              # MongoDB schemas
│       ├── UserModels.js
│       ├── ReportModels.js
│       ├── ChatBotModels.js
│       └── VaultModels.js
├── middleware/              # Request validators
│   ├── auth.js              # JWT authentication
│   ├── chatbot.js           # Chatbot validation
│   ├── extraction.js        # File upload validation
│   └── upload.js            # Multer file handler
├── routes/                  # API endpoints
│   ├── authRoutes.js
│   ├── chatbotRoutes.js
│   └── extractionRoutes.js
├── services/
│   └── agentService.js      # Python agent integration
├── uploads/                 # Temporary file storage
├── app.js                   # Express app configuration
├── server.js                # Server entry point
└── package.json             # Dependencies

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `config/.env`:
```env
PORT=5000
MONGODB_URL=mongodb://localhost:27017/smart_medical_analyser
JWT_SECRET=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Start Server
```bash
npm run dev     # Development mode with nodemon
npm start       # Production mode
```

## 🔌 API Endpoints

### Authentication
- `POST /api/users/register` - Create new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile (protected)

### Report Extraction
- `POST /api/extraction/extract` - Upload & extract PDF report
- `GET /api/extraction/reports` - List user reports
- `GET /api/extraction/report/:id` - Get specific report
- `DELETE /api/extraction/report/:id` - Delete report

### Medical Chatbot
- `POST /api/chat/start` - Initialize chat session
- `POST /api/chat/message` - Send message to chatbot
- `GET /api/chat/history/:chatId` - Get conversation history
- `GET /api/chat/sessions` - List all chat sessions
- `DELETE /api/chat/session/:chatId` - Delete chat session

## 🔐 Authentication

All protected routes require JWT token in header:
```
Authorization: Bearer <your_jwt_token>
```

## 📦 Dependencies

### Core
- **express** - Web framework
- **mongoose** - MongoDB ODM
- **jsonwebtoken** - Authentication
- **bcryptjs** - Password hashing

### File Processing
- **multer** - File upload handling
- **pdf-parse** - PDF text extraction

### Utilities
- **dotenv** - Environment variables
- **cors** - Cross-origin requests
- **morgan** - HTTP logging

## 🏗️ Architecture

### MVC Pattern
- **Models**: MongoDB schemas (Database/Models/)
- **Views**: JSON responses
- **Controllers**: Business logic (controllers/)

### Middleware Stack
1. CORS handling
2. Body parsing (JSON, URL-encoded)
3. Authentication (JWT)
4. Request validation
5. Error handling

### Python Integration
- Spawns Python processes for ML tasks
- Communicates via stdin/stdout
- Automatic model failover for Gemini API

## 🛠️ Development

### Code Standards
- ES6+ JavaScript
- Async/await for asynchronous operations
- Error-first callbacks
- RESTful API design

### File Organization
- One feature per controller
- Middleware for reusable logic
- Services for external integrations
- Models for data schemas

## 📊 Database Schema

### User
- Credentials (email, password)
- Profile information
- Timestamps

### Report
- User reference
- Extracted lab test data
- AI-generated summary
- Risk level assessment

### ChatBot
- User & report references
- Conversation history
- Message timestamps

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 5000 |
| MONGODB_URL | MongoDB connection string | localhost:27017 |
| JWT_SECRET | Secret for JWT signing | - |
| JWT_EXPIRE | Token expiration time | 30d |
| GEMINI_API_KEY | Google Gemini API key | - |
| MAX_FILE_SIZE | Max upload size (bytes) | 10485760 |

## 🚨 Error Handling

All endpoints return standardized error responses:
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error (dev mode only)"
}
```

## 📝 Logging

- HTTP requests logged via Morgan
- Python integration logs to stderr
- Model failover logs visible in console

## 🧪 Testing

Test chatbot integration:
```bash
# From Backend directory
node test_chatbot_integration.js
```

## 🔒 Security

- Passwords hashed with bcrypt (10 rounds)
- JWT for stateless authentication
- File upload size limits
- Request rate limiting on chatbot
- Input validation on all endpoints

## 📈 Performance

- MongoDB indexing on user & report queries
- Chat history limited to last 20 messages
- Automatic cleanup of temp files
- Connection pooling for database

## 🐛 Troubleshooting

### MongoDB Connection Failed
- Check MongoDB is running: `mongod`
- Verify MONGODB_URL in .env

### Python Integration Errors
- Ensure Python 3.10+ installed
- Install dependencies: `pip install -r requirements.txt`
- Check ChatBotAgent folder exists

### API Key Quota Exceeded
- Model failover tries 4 different models
- Wait 1-2 minutes for quota reset
- Get new API key from: https://aistudio.google.com/apikey

## 📚 Additional Resources

- [Express Documentation](https://expressjs.com/)
- [Mongoose Guide](https://mongoosejs.com/)
- [JWT Introduction](https://jwt.io/)
- [Gemini API](https://ai.google.dev/docs)
