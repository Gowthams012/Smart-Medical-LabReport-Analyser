# Testing Checklist ✅

Use this checklist to verify all components are working correctly.

## 🔧 Environment Setup

- [ ] Node.js v22+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version`)
- [ ] MongoDB running (`mongosh` connects successfully)
- [ ] Backend dependencies installed (`npm install` in Backend/)
- [ ] Python dependencies installed (see main requirements.txt)

## 🗄️ Database

- [ ] MongoDB running on localhost:27017
- [ ] Can connect to `Smart-Lab-Analyser` database
- [ ] Collections exist: user, report, vault, chatbot
- [ ] Database connection in backend works

## 🚀 Backend Server

- [ ] Server starts without errors (`npm run dev`)
- [ ] Sees "Server running on port 5000"
- [ ] Sees "MongoDB Connected"
- [ ] Health check works: GET `http://localhost:5000/` returns "✅ Smart Medical Lab Report Analyzer API Running"

## 🔐 Authentication

- [ ] **POST /api/auth/signup**
  - [ ] Creates new user
  - [ ] Returns JWT token
  - [ ] Password is hashed in database
  
- [ ] **POST /api/auth/login**
  - [ ] Logs in existing user
  - [ ] Returns valid JWT token
  - [ ] Invalid password rejected
  
- [ ] **GET /api/auth/me**
  - [ ] Works with valid token
  - [ ] Returns user profile
  - [ ] Fails without token (401)

## 📄 PDF Upload & Processing

- [ ] **POST /api/extraction/upload**
  - [ ] Accepts PDF file
  - [ ] Requires authentication
  - [ ] Rejects non-PDF files
  - [ ] Saves to `Backend/uploads/{userId}/`
  
- [ ] **VaultAgent Integration**
  - [ ] Successfully identifies patient name
  - [ ] Creates/updates patient vault folder
  - [ ] Copies PDF to `integrated_output/PatientVaults/{patientName}/`
  
- [ ] **ExtractionAgent Integration**
  - [ ] Extracts medical data from PDF
  - [ ] Creates JSON file in `integrated_output/extractions/`
  - [ ] Returns test count and patient info
  - [ ] JSON file is valid and readable
  
- [ ] **SummaryAgent Integration**
  - [ ] Generates clinical summary
  - [ ] Creates text file in `summary_output/`
  - [ ] Summary is human-readable
  - [ ] Contains relevant medical insights
  
- [ ] **RecommendationAgent Integration**
  - [ ] Generates medical recommendations
  - [ ] Creates markdown file in `medical_recommendations/`
  - [ ] Recommendations are formatted properly
  - [ ] Contains actionable medical advice

## 💾 Data Storage

- [ ] **Report Document Created**
  - [ ] Saved to MongoDB `report` collection
  - [ ] Contains extractedData object
  - [ ] Contains summary string
  - [ ] Contains recommendations string
  - [ ] patientName auto-detected
  - [ ] riskLevel determined
  - [ ] Linked to correct userID
  
- [ ] **Vault Document Updated**
  - [ ] Created/updated in `vault` collection
  - [ ] File metadata stored correctly
  - [ ] reportId linked to Report
  - [ ] patientName recorded
  - [ ] status set to "processed"

## 📋 Report Management

- [ ] **GET /api/extraction/reports**
  - [ ] Returns all user reports
  - [ ] Only shows current user's reports
  - [ ] Sorted by date (newest first)
  - [ ] Excludes extractedData (performance)
  
- [ ] **GET /api/extraction/reports/:id**
  - [ ] Returns specific report
  - [ ] Includes full extractedData
  - [ ] Only accessible by owner
  - [ ] Returns 404 for invalid ID
  
- [ ] **DELETE /api/extraction/reports/:id**
  - [ ] Deletes report from database
  - [ ] Only owner can delete
  - [ ] Returns success message

## 🧪 Integration Testing

- [ ] **test-agent-integration.js**
  - [ ] Runs without errors
  - [ ] Processes sample PDF
  - [ ] All agents complete successfully
  - [ ] Output files created
  - [ ] Prints success message

- [ ] **End-to-End Test**
  - [ ] Signup → Login → Upload → Get Reports
  - [ ] Complete flow works
  - [ ] Data persists in MongoDB
  - [ ] Files created in correct locations

## 📁 Output Files Verification

- [ ] `Backend/uploads/{userId}/` contains uploaded PDF
- [ ] `integrated_output/extractions/{session}/json/` contains medical JSON
- [ ] `integrated_output/PatientVaults/{patientName}/` contains patient PDF
- [ ] `summary_output/` contains clinical summary text file
- [ ] `medical_recommendations/` contains protocol markdown file

## 🎯 Performance

- [ ] Full processing completes in 15-30 seconds
- [ ] No memory leaks during multiple uploads
- [ ] Server responds quickly to API requests
- [ ] Database queries are fast (<100ms)

## 🔒 Security

- [ ] Passwords are hashed (not plain text in DB)
- [ ] JWT tokens expire appropriately
- [ ] Protected routes require authentication
- [ ] Users can only access own data
- [ ] File upload size limited to 10MB
- [ ] Only PDF files accepted

## 📊 MongoDB Data Integrity

Check in MongoDB Compass or mongosh:

- [ ] **user collection**
  ```javascript
  db.user.findOne()
  // Should have: email, username, password (hashed), createdAt
  ```

- [ ] **report collection**
  ```javascript
  db.report.findOne()
  // Should have: userID, patientName, extractedData, summary, recommendations, riskLevel
  ```

- [ ] **vault collection**
  ```javascript
  db.vault.findOne()
  // Should have: userID, files array with file metadata
  ```

## 🐛 Error Handling

- [ ] Invalid login credentials rejected
- [ ] Missing required fields return 400
- [ ] Invalid PDF returns error
- [ ] Agent failures return 500 with message
- [ ] Database errors handled gracefully
- [ ] Missing files return 404

## 📝 Console Logs

Check that logs are informative:

- [ ] VaultAgent: "🔍 VaultAgent: Identifying patient..."
- [ ] ExtractionAgent: "🔬 ExtractionAgent: Extracting medical data..."
- [ ] SummaryAgent: "📝 SummaryAgent: Generating clinical summary..."
- [ ] RecommendationAgent: "💊 RecommendationAgent: Generating recommendations..."
- [ ] Success: "✅ Complete pipeline finished successfully!"
- [ ] Errors: "❌ Pipeline failed: [error message]"

## 🎓 Final Verification

Run this complete test sequence:

1. **Start fresh**
   ```bash
   # Clear database (optional)
   mongosh
   use Smart-Lab-Analyser
   db.dropDatabase()
   ```

2. **Start server**
   ```bash
   cd Backend
   npm run dev
   ```

3. **Create account** (Postman)
   - POST /api/auth/signup
   - Save token

4. **Upload PDF** (Postman)
   - POST /api/extraction/upload
   - Use sample PDF from `data/pdfs/`
   - Wait for completion (~20 seconds)

5. **Verify response**
   - success: true
   - reportId present
   - patientName detected
   - testCount > 0
   - summary present
   - recommendations present

6. **Check database**
   - report document exists
   - vault document exists
   - All fields populated

7. **Check files**
   - All output directories have files
   - JSON is valid
   - Summary is readable
   - Recommendations formatted

8. **Get reports** (Postman)
   - GET /api/extraction/reports
   - Should see uploaded report

9. **Get report details** (Postman)
   - GET /api/extraction/reports/:id
   - Full data returned

If all checks pass: **🎉 Everything is working perfectly!**

---

## 📸 Expected Success Output

When uploading PDF, console should show:

```
📥 Processing report for user: 6789abc...
   File: 20415.pdf
   Path: C:\...\uploads\6789abc...\1234567890_20415.pdf

🔍 VaultAgent: Identifying patient...
✅ Patient identified: GOWTHAMS

🔬 ExtractionAgent: Extracting medical data...
✅ Data extraction complete
   Tests found: 25
   Patient: GOWTHAMS
   File: integrated_output/extractions/...

⚡ Running Summary & Recommendation agents in parallel...
📝 SummaryAgent: Generating clinical summary...
💊 RecommendationAgent: Generating recommendations...
✅ Summary generated
   File: summary_output/...
✅ Recommendations generated
   File: medical_recommendations/...

✅ Complete pipeline finished successfully!

📊 Creating report in database...
✅ Report saved to database: 6789def...
```

---

**Use this checklist systematically to ensure everything works! ✨**
