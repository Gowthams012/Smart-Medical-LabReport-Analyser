# Smart Medical Analyser - Production Setup

## Overview
Complete medical report analysis system with MongoDB backend, Python AI agents, and REST API.

## Architecture
- **Backend**: Node.js + Express + MongoDB
- **AI Agents**: Python (ExtractionAgent, InsightAgent, VaultAgent)
- **Database**: MongoDB for user auth, reports, and patient vaults
- **AI Service**: Google Gemini API for clinical insights

## Prerequisites
- Node.js v22.13.1 or higher
- Python 3.8+ with pip
- MongoDB (local or cloud)
- Google Gemini API key

## Installation

### 1. Install Node.js Dependencies
```bash
cd Backend
npm install
```

### 2. Install Python Dependencies
```bash
# Install for ExtractionAgent
cd ExtractionAgent
pip install -r requirements.txt

# Install for InsightAgent (Summary & Recommendations)
cd ../InsightAgent
pip install google-generativeai

# Install for VaultAgent
cd ../ValutAgent
pip install -r requirements.txt

# Install for ChatBotAgent (optional)
cd ../ChatBotAgent
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Edit `Backend/config/.env`:
```env
MONGODB_URL = mongodb://localhost:27017/Smart-Lab-Analyser
PORT = 5000
JWT_SECRET = your_secure_jwt_secret_here
JWT_EXPIRE = 30d
GOOGLE_GEMINI_API_KEY = your_gemini_api_key_here
```

**IMPORTANT**: Replace `your_gemini_api_key_here` with your actual Google Gemini API key from https://makersuite.google.com/app/apikey

### 4. Start MongoDB
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

## Running the Application

### Development Mode
```bash
cd Backend
npm run dev
```
Server starts on http://localhost:5000

### Production Mode
```bash
cd Backend
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires JWT)
- `POST /api/auth/logout` - Logout user

### Report Processing
- `POST /api/extraction/upload` - Upload PDF medical report
- `GET /api/extraction/reports` - Get all user reports
- `GET /api/extraction/reports/:id` - Get specific report
- `DELETE /api/extraction/reports/:id` - Delete report

## Testing with Postman

1. Import `Backend/Postman_API_Collection.json` into Postman

2. **Signup**: POST to `/api/auth/signup`
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "securepassword123"
   }
   ```

3. **Login**: POST to `/api/auth/login`
   ```json
   {
     "email": "test@example.com",
     "password": "securepassword123"
   }
   ```
   Copy the `token` from response.

4. **Upload PDF**: POST to `/api/extraction/upload`
   - Authorization: Bearer {your_token}
   - Body: form-data
   - Key: `pdfFile` (type: File)
   - Value: Select your PDF medical report

## Workflow

1. **User uploads PDF** → Backend receives file
2. **ExtractionAgent** → Extracts medical data (tests, values, results)
3. **InsightAgent - Summary** → Generates clinical summary using Gemini AI
4. **InsightAgent - Recommendations** → Generates medical recommendations
5. **VaultAgent** → Identifies patient and segregates PDF into patient folder
6. **Database** → Saves report metadata to MongoDB

## Output Structure

```
integrated_output/
  ├── extractions/
  │   └── {timestamp}/
  │       └── {reportId}/
  │           └── json/
  │               ├── {reportId}_complete_data.json
  │               └── {reportId}_medical_report.json
  └── PatientVaults/
      └── {patientName}/
          └── {reportId}/
              └── {originalFilename}.pdf

summary_output/
  └── {timestamp}_{reportId}_medical_report_summary_{timestamp}.txt

medical_recommendations/
  └── PROTOCOL_{timestamp}_{reportId}_medical_report_{date}.md
```

## MongoDB Collections

- **user**: User authentication (email, username, password)
- **report**: Medical reports (patientName, testCount, riskLevel, summary, recommendations)
- **vault**: Patient file vaults (userID, patientName, files array)
- **chatbot**: Chat history (future use)

## Security Notes

⚠️ **PRODUCTION CHECKLIST**:
1. Change `JWT_SECRET` to a strong random string (at least 32 characters)
2. Use environment variables for all sensitive data
3. Enable CORS only for trusted domains
4. Set up HTTPS/SSL for production deployment
5. Use MongoDB authentication (username/password)
6. Rotate API keys regularly
7. Implement rate limiting for API endpoints
8. Add input validation and sanitization
9. Set up logging and monitoring

## Troubleshooting

### Python Encoding Errors (Windows)
If you see Unicode errors, ensure `PYTHONIOENCODING: 'utf-8'` is set in `agentService.js` (already configured).

### MongoDB Connection Failed
- Check MongoDB service is running
- Verify connection string in `.env`
- Check firewall settings

### API Key Errors
- Ensure `GOOGLE_GEMINI_API_KEY` is set in `.env`
- Verify key is valid at https://makersuite.google.com
- Check API quota hasn't been exceeded

### File Upload Errors
- Ensure form-data key is exactly `pdfFile`
- Check file size is under 10MB
- Verify file type is PDF

## Project Structure

```
Smart-Medical-Analyser/
├── Backend/                    # Node.js Express server
│   ├── config/                 # Configuration (.env)
│   ├── controllers/            # Route controllers
│   ├── Database/
│   │   └── Models/             # Mongoose schemas
│   ├── middleware/             # Auth, upload middleware
│   ├── routes/                 # API routes
│   ├── services/               # Agent integration
│   └── server.js               # Entry point
├── ExtractionAgent/            # PDF → JSON extraction
├── InsightAgent/               # Summary & Recommendations (Gemini AI)
│   ├── Summary.py
│   └── Recommendation.py
├── VaultAgent/                 # Patient identification & segregation
└── ChatBotAgent/               # Future chatbot feature
```

## Support

For issues or questions:
1. Check logs in terminal where server is running
2. Review MongoDB logs
3. Check Python agent output in console
4. Verify all dependencies are installed

## License
[Your License Here]
