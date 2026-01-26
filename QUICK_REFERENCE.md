# Quick Reference Guide

## 🚀 Starting the System

```bash
# 1. Start MongoDB
net start MongoDB

# 2. Start Backend Server (Development)
cd Backend
npm run dev

# Server runs on: http://localhost:5000
```

---

## 📋 Common API Calls

### 1. User Signup
```http
POST http://localhost:5000/api/auth/signup
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123"
}
```

### 2. User Login
```http
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "securepassword123"
}

Response: { "token": "eyJhbGciOiJ..." }
```

### 3. Upload PDF Report
```http
POST http://localhost:5000/api/extraction/upload
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: multipart/form-data

Form Data:
  pdfFile: [Select PDF file]
```

### 4. Get All Reports
```http
GET http://localhost:5000/api/extraction/reports
Authorization: Bearer YOUR_TOKEN_HERE
```

### 5. Get Specific Report
```http
GET http://localhost:5000/api/extraction/reports/:reportId
Authorization: Bearer YOUR_TOKEN_HERE
```

### 6. Delete Report
```http
DELETE http://localhost:5000/api/extraction/reports/:reportId
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 🐍 Testing Python Agents Individually

### ExtractionAgent
```bash
cd ExtractionAgent
python ExtractionAgent.py
# Or test via main.py in root
```

### Summary Agent
```bash
cd InsightAgent
set GOOGLE_GEMINI_API_KEY=your_api_key_here
python Summary.py path/to/medical_report.json
```

### Recommendation Agent
```bash
cd InsightAgent
set GOOGLE_GEMINI_API_KEY=your_api_key_here
python Recommendation.py path/to/medical_report.json
```

### VaultAgent
```bash
cd VaultAgent
python VaultAgent.py
```

---

## 🗄️ MongoDB Commands

### Connect to Database
```bash
mongosh
use Smart-Lab-Analyser
```

### View Collections
```javascript
show collections
// Output: user, report, vault, chatbot
```

### Count Documents
```javascript
db.user.countDocuments()
db.report.countDocuments()
db.vault.countDocuments()
```

### Find All Users
```javascript
db.user.find().pretty()
```

### Find Reports for Specific User
```javascript
db.report.find({ userID: ObjectId("USER_ID_HERE") }).pretty()
```

### Delete All Test Data
```javascript
db.user.deleteMany({})
db.report.deleteMany({})
db.vault.deleteMany({})
```

---

## 🔧 Troubleshooting

### Issue: "MongoDB connection failed"
```bash
# Check if MongoDB is running
sc query MongoDB

# If not running, start it
net start MongoDB
```

### Issue: "Module not found" (Node.js)
```bash
cd Backend
npm install
```

### Issue: "No module named 'xyz'" (Python)
```bash
cd ExtractionAgent
pip install -r requirements.txt

cd ../InsightAgent
pip install google-generativeai

cd ../VaultAgent
pip install -r requirements.txt
```

### Issue: "API key error" (Gemini)
```bash
# Make sure .env has the key
cd Backend/config
notepad .env

# Add: GOOGLE_GEMINI_API_KEY = your_actual_key_here
```

### Issue: "File not found after upload"
Check logs - path resolution should be working now. If not:
1. Verify `os.chdir()` is in agentService.js
2. Check Python agents return absolute paths
3. Look at console output for exact error

---

## 📁 Output File Locations

### Extracted Data
```
integrated_output/extractions/{timestamp}/{reportId}/json/
  - {reportId}_complete_data.json
  - {reportId}_medical_report.json
```

### Summary
```
summary_output/
  - {timestamp}_{reportId}_medical_report_summary_{timestamp}.txt
```

### Recommendations
```
medical_recommendations/
  - PROTOCOL_{timestamp}_{reportId}_medical_report_{date}.md
```

### Patient Vaults
```
integrated_output/PatientVaults/{patientName}/{reportId}/
  - {original_filename}.pdf
```

---

## 🎯 Complete Workflow Test

```bash
# 1. Start system
net start MongoDB
cd Backend
npm run dev

# 2. In Postman:
#    - Import Backend/Postman_API_Collection.json
#    - Run "Signup" request
#    - Run "Login" request
#    - Copy the token from response
#    - In "Upload Report", add token to Authorization header
#    - Select a PDF file
#    - Send request

# 3. Check response (should include):
#    - reportId
#    - patientName
#    - testCount
#    - riskLevel
#    - summary (AI-generated text)
#    - recommendations (AI-generated markdown)

# 4. Verify files created:
dir summary_output
dir medical_recommendations
dir integrated_output\PatientVaults
```

---

## 🔑 Environment Variables (.env)

Required in `Backend/config/.env`:
```env
MONGODB_URL = mongodb://localhost:27017/Smart-Lab-Analyser
PORT = 5000
JWT_SECRET = your_secure_random_string_minimum_32_characters
JWT_EXPIRE = 30d
GOOGLE_GEMINI_API_KEY = your_gemini_api_key_from_google
```

---

## 📊 Response Time Expectations

| Operation | Expected Time |
|-----------|---------------|
| Signup/Login | < 500ms |
| File Upload (save only) | < 1s |
| ExtractionAgent | 2-5s |
| SummaryAgent (Gemini API) | 5-10s |
| RecommendationAgent (Gemini API) | 5-10s |
| VaultAgent | 1-2s |
| **Total Pipeline** | **15-30s** |

---

## 🛡️ Security Checklist

Before Production:
- [ ] Change JWT_SECRET to strong random string
- [ ] Use production MongoDB (MongoDB Atlas)
- [ ] Enable MongoDB authentication
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for specific domains only
- [ ] Add rate limiting
- [ ] Enable logging and monitoring
- [ ] Rotate API keys regularly

---

## 📞 Getting Help

1. Check `PRODUCTION_README.md` for setup details
2. Check `DEPLOYMENT_CHECKLIST.md` before deployment
3. Check `PRODUCTION_STATUS.md` for what's been fixed
4. Review server logs in terminal
5. Check MongoDB logs: `C:\Program Files\MongoDB\Server\{version}\log\`
6. Test with sample PDF in `data/pdfs/`

---

**Quick Start**: See `PRODUCTION_README.md`
**Deployment**: See `DEPLOYMENT_CHECKLIST.md`
**Status**: See `PRODUCTION_STATUS.md`
