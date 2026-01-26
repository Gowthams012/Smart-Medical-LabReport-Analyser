# Smart Medical Lab Report Analyzer - Backend

Complete Node.js backend with Python agent integration for automated medical report processing.

## 🏗️ Architecture

```
User Upload PDF → Node.js Backend → Python Agents → MongoDB
                       ↓
    ┌──────────────────┴──────────────────┐
    │                                      │
    ▼                                      ▼
VaultAgent                          ExtractionAgent
(Patient ID)                        (Extract Data)
                                          ↓
                                    ┌─────┴─────┐
                                    ▼           ▼
                              SummaryAgent  RecommendationAgent
                              (Insights)    (Protocol)
                                    │           │
                                    └─────┬─────┘
                                          ▼
                                      Save to DB
```

## 📁 Project Structure

```
Backend/
├── app.js                          # Express app configuration
├── server.js                       # Server startup
├── package.json                    # Dependencies
│
├── Database/
│   ├── databaseConnections.js     # MongoDB connection
│   └── Models/
│       ├── UserModels.js           # User schema
│       ├── ReportModels.js         # Report schema
│       ├── VaultModels.js          # Vault schema
│       └── ChatBotModels.js        # ChatBot schema
│
├── controllers/
│   ├── authController.js           # Authentication logic
│   └── extractionController.js    # PDF upload & processing
│
├── routes/
│   ├── authRoutes.js               # Auth endpoints
│   └── extractionRoutes.js        # Report endpoints
│
├── middleware/
│   ├── auth.js                     # JWT verification
│   └── upload.js                   # Multer file upload
│
├── services/
│   └── agentService.js            # Python agent integration
│
└── uploads/                        # User uploaded files
    └── {userId}/                   # Per-user directories
```

## 🚀 Setup & Installation

### Prerequisites
- Node.js v22+ 
- Python 3.10+
- MongoDB running on localhost:27017
- Python dependencies installed (see main README)

### Install Dependencies
```bash
cd Backend
npm install
```

### Environment Configuration
Create `.env` file in Backend directory:
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017/smart-lab-analyser

# JWT Secret (change this!)
JWT_SECRET=your_super_secret_jwt_key_here

# Server
PORT=5000
NODE_ENV=development
```

## 🏃‍♂️ Running the Server

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

Server will start on `http://localhost:5000`

## 🧪 Testing

### Test Agent Integration
```bash
node test-agent-integration.js
```
This will test the complete pipeline with a sample PDF from `data/pdfs/`

### Import Postman Collection
1. Open Postman
2. Import `Postman_API_Collection.json`
3. Test endpoints:
   - Sign up / Login
   - Upload PDF report
   - Get reports

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/signup      # Create account
POST   /api/auth/login       # Login
GET    /api/auth/me          # Get current user (protected)
```

### Report Processing
```
POST   /api/extraction/upload          # Upload PDF & process
GET    /api/extraction/reports         # Get all user reports
GET    /api/extraction/reports/:id     # Get specific report
DELETE /api/extraction/reports/:id     # Delete report
```

## 🔄 PDF Processing Flow

1. **Upload** - User uploads PDF via multipart/form-data
2. **VaultAgent** - Identifies patient name from PDF
3. **ExtractionAgent** - Extracts medical data (tests, values, ranges)
4. **Parallel Processing:**
   - SummaryAgent generates clinical summary
   - RecommendationAgent generates medical protocol
5. **Save to MongoDB** - Store all data with references
6. **Update Vault** - Track file in user's vault

## 🐍 Python Agent Integration

### How It Works
The `agentService.js` calls Python agents as-is without modification:

```javascript
// Example: Extract data
const result = await agentService.extractData(pdfPath);
// Calls ExtractionAgent.quick_process()
// Reads JSON output from integrated_output/extractions/
```

### Agent Outputs
- **ExtractionAgent** → `integrated_output/extractions/{session}/json/`
- **SummaryAgent** → `summary_output/{filename}.txt`
- **RecommendationAgent** → `medical_recommendations/{filename}.md`
- **VaultAgent** → `integrated_output/PatientVaults/{patientName}/`

## 📊 Database Schema

### User Collection
```javascript
{
  email: String (unique),
  username: String,
  password: String (hashed),
  googleId: String (optional)
}
```

### Report Collection
```javascript
{
  userID: ObjectId (ref User),
  patientName: String (auto-detected),
  reportType: String,
  extractedData: Object,      // Full JSON from ExtractionAgent
  summary: String,             // Clinical summary
  recommendations: String,     // Medical protocol (markdown)
  riskLevel: 'Normal' | 'Medium' | 'High' | 'Unknown'
}
```

### Vault Collection
```javascript
{
  userID: ObjectId (ref User, unique),
  files: [{
    fileName: String,
    fileType: String,
    fileSize: Number,
    fileURL: String,
    status: 'uploaded' | 'processed' | 'failed',
    reportId: ObjectId (ref Report),
    patientName: String
  }]
}
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Protected routes with auth middleware
- File upload size limit (10MB)
- PDF-only file filter
- User-isolated file storage

## 🛠️ Development

### Add New Route
1. Create controller in `controllers/`
2. Create route file in `routes/`
3. Register in `app.js`

### Modify Agent Integration
Edit `services/agentService.js` - all Python agent calls are centralized here.

## 📝 Notes

- **No Agent Modification**: Python agents are called as-is, outputs are read from disk
- **Parallel Processing**: Summary and Recommendations run simultaneously for speed
- **Auto Patient Detection**: VaultAgent automatically identifies patient from PDF
- **MongoDB Collections**: Using singular names (user, report, vault, chatbot)
- **File Organization**: User uploads organized by userId, agent outputs by session

## 🐛 Troubleshooting

### "Module not found" error
```bash
npm install
```

### "Cannot connect to MongoDB"
Ensure MongoDB is running:
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### "Python not found"
Verify Python is in PATH:
```bash
python --version
```

### Agent errors
Test agents individually:
```bash
cd ..
python ExtractionAgent/ExtractionAgent.py --pdf data/pdfs/sample.pdf
```

## 📚 Additional Resources

- [Express.js Documentation](https://expressjs.com/)
- [Mongoose Documentation](https://mongoosejs.com/)
- [Multer Documentation](https://github.com/expressjs/multer)
- [JWT Best Practices](https://jwt.io/)

---

**Built with ❤️ for automated medical report analysis**
