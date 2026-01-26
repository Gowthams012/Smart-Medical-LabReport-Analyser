# Smart Medical Analyser - Project Structure

## 📂 Directory Layout

```
Smart-Medical-Analyser/
│
├── Backend/                           # Node.js REST API Server
│   ├── config/
│   │   └── .env                       # Environment variables
│   ├── controllers/                   # Business logic layer
│   │   ├── authController.js          # User authentication
│   │   ├── chatbotController.js       # Medical chatbot
│   │   └── extractionController.js    # PDF processing
│   ├── Database/
│   │   └── Models/                    # MongoDB schemas
│   │       ├── UserModels.js
│   │       ├── ReportModels.js
│   │       ├── ChatBotModels.js
│   │       └── VaultModels.js
│   ├── middleware/                    # Request validators
│   │   ├── auth.js                    # JWT authentication
│   │   ├── chatbot.js                 # Chatbot validation
│   │   ├── extraction.js              # File validation
│   │   └── upload.js                  # File upload handler
│   ├── routes/                        # API endpoints
│   │   ├── authRoutes.js
│   │   ├── chatbotRoutes.js
│   │   └── extractionRoutes.js
│   ├── services/
│   │   └── agentService.js            # Python integration
│   ├── uploads/                       # Temporary files
│   ├── app.js                         # Express configuration
│   ├── server.js                      # Server entry point
│   ├── package.json                   # Dependencies
│   └── README.md                      # Backend documentation
│
├── ChatBotAgent/                      # Python Medical Chatbot
│   └── ChatBot.py                     # AI chatbot with model failover
│
├── ExtractionAgent/                   # PDF Data Extraction
│   └── (extraction scripts)
│
├── InsightAgent/                      # Medical Analysis
│   ├── Recommendation.py              # Medical recommendations
│   ├── Summary.py                     # Report summarization
│   └── root.py                        # Agent orchestration
│
├── ValutAgent/                        # Data vault management
│
├── data/                              # Sample data
├── integrated_output/                 # Processed reports
├── medical_recommendations/           # Generated recommendations
├── summary_output/                    # Generated summaries
│
├── .gitignore                         # Git ignore rules
├── main.py                            # Python entry point
└── README.md                          # Project documentation

## 🔧 Technology Stack

### Backend (Node.js)
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Database**: MongoDB
- **Authentication**: JWT
- **File Processing**: Multer, PDF-Parse

### AI/ML (Python)
- **Language**: Python 3.10+
- **AI Models**: Google Gemini (with auto-failover)
- **Libraries**: google-generativeai, json, tempfile

### Database
- **Type**: NoSQL (MongoDB)
- **ODM**: Mongoose
- **Collections**: users, reports, chatbots, vaults

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- MongoDB 6.0+
- Google Gemini API Key

### Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd Smart-Medical-Analyser
   ```

2. **Backend Setup**
   ```bash
   cd Backend
   npm install
   cp config/.env.example config/.env
   # Edit .env with your credentials
   npm run dev
   ```

3. **Python Dependencies**
   ```bash
   pip install google-generativeai
   ```

4. **MongoDB**
   ```bash
   mongod --dbpath /path/to/data
   ```

## 📡 API Architecture

### RESTful Endpoints
- **Authentication**: `/api/users/*`
- **Reports**: `/api/extraction/*`
- **Chatbot**: `/api/chat/*`

### Data Flow
```
PDF Upload → Extraction Agent → MongoDB → Summary/Recommendations
                                    ↓
User Question → ChatBot Agent → Gemini AI → Response
```

### Python Integration
- Node.js spawns Python processes
- Data passed via stdin/stdout
- Automatic model failover for resilience

## 🗂️ Key Features

### 1. Medical Report Extraction
- PDF parsing
- Structured data extraction
- Automatic test result categorization

### 2. AI-Powered Chatbot
- Context-aware medical Q&A
- Personalized health advice
- Safety guardrails (no diagnosis/prescriptions)
- Automatic model failover

### 3. Medical Insights
- Lab result summarization
- Risk assessment
- Dietary recommendations
- Lifestyle suggestions

### 4. User Management
- Secure authentication
- Report history
- Chat session management

## 🔐 Security

- Bcrypt password hashing
- JWT token authentication
- File upload validation
- Rate limiting on chatbot
- Input sanitization
- MongoDB injection prevention

## 📊 Database Schema

### Users
- Credentials & profile
- Report references
- Chat history

### Reports
- Extracted lab data
- AI-generated insights
- Risk level assessment

### ChatBots
- Conversation history
- Report context
- User associations

## 🛠️ Development

### Code Standards
- ES6+ JavaScript (Backend)
- PEP 8 Python style
- RESTful API design
- MVC architecture

### Project Organization
- Feature-based structure
- Separation of concerns
- Reusable middleware
- Service layer for integrations

## 🧪 Testing

### Backend
```bash
cd Backend
npm test
```

### Python Agents
```bash
python test_chatbot_integration.py
python test_model_failover.py
```

## 📈 Performance

- MongoDB indexing
- Connection pooling
- File upload limits (10MB)
- Chat history pruning (20 messages)
- Automatic temp file cleanup

## 🐛 Troubleshooting

### Common Issues

**MongoDB Connection**
- Check MongoDB is running
- Verify MONGODB_URL in .env

**Python Errors**
- Ensure Python 3.10+
- Install google-generativeai
- Check GEMINI_API_KEY

**API Quota Exceeded**
- Automatic failover tries 4 models
- Wait 1-2 minutes
- Get new API key if needed

## 📝 Environment Variables

Required in `Backend/config/.env`:
```env
PORT=5000
MONGODB_URL=mongodb://localhost:27017/smart_medical_analyser
JWT_SECRET=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

## 📚 Documentation

- **Backend API**: See `Backend/README.md`
- **ChatBot**: See `ChatBotAgent/ChatBot.py` docstrings
- **Models**: Check `Backend/Database/Models/`

## 🤝 Contributing

1. Follow existing code structure
2. Add comments for complex logic
3. Update README when adding features
4. Test before committing

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Check logs for errors

---

**Last Updated**: January 26, 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
