# Quick Start Guide 🚀

Get the Smart Medical Analyzer backend running in 5 minutes!

## Prerequisites Check

```bash
# Check Node.js (need v22+)
node --version

# Check Python (need 3.10+)
python --version

# Check MongoDB is running
# Windows: services.msc → look for MongoDB
# Linux/Mac: systemctl status mongod
```

## Step 1: Install Backend Dependencies

```bash
cd Backend
npm install
```

## Step 2: Configure Environment

The `.env` file is already configured in `Backend/config/.env`:
```env
MONGODB_URL = mongodb://localhost:27017/Smart-Lab-Analyser
PORT = 5000
JWT_SECRET = your_jwt_secret_key_here_change_in_production
```

✅ No changes needed for local development!

## Step 3: Start the Server

```bash
npm run dev
```

You should see:
```
🚀 Server running on port 5000
✅ MongoDB Connected: Smart-Lab-Analyser
```

## Step 4: Test with Postman

### Import Collection
1. Open Postman
2. File → Import
3. Select `Backend/Postman_API_Collection.json`

### Test Authentication
1. **Signup** - Create account
2. **Login** - Get JWT token (auto-saved)
3. **Get Me** - Verify authentication

### Test PDF Upload
1. Select **Upload PDF Report** request
2. In Body → form-data, select file:
   - Click on file input
   - Browse to `data/pdfs/20415.pdf`
3. Send request

Expected response (~15-20 seconds):
```json
{
  "success": true,
  "message": "Report processed successfully",
  "data": {
    "reportId": "...",
    "patientName": "Auto-detected name",
    "testCount": 25,
    "riskLevel": "Normal",
    "summary": "Clinical summary...",
    "recommendations": "Medical protocol..."
  }
}
```

## Step 5: Verify Data in MongoDB

### Option A: MongoDB Compass
1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Open database `Smart-Lab-Analyser`
4. Check collections:
   - `user` - Your account
   - `report` - Processed reports
   - `vault` - File tracking

### Option B: Command Line
```bash
mongosh
use Smart-Lab-Analyser
db.report.find().pretty()
db.vault.find().pretty()
```

## 🎯 What Just Happened?

When you uploaded the PDF:

1. **VaultAgent** identified the patient name
2. **ExtractionAgent** extracted all medical test data
3. **SummaryAgent** generated clinical insights
4. **RecommendationAgent** created medical protocol
5. Everything saved to MongoDB

## 📂 Check Output Files

```bash
# Extracted JSON data
ls integrated_output/extractions/

# Patient-segregated PDFs
ls integrated_output/PatientVaults/

# Clinical summaries
ls summary_output/

# Medical recommendations
ls medical_recommendations/
```

## 🧪 Test Agent Integration Only

Want to test Python agents without the server?

```bash
cd Backend
node test-agent-integration.js
```

This runs the complete pipeline with a sample PDF.

## 📡 API Endpoints Reference

```
Authentication:
POST   /api/auth/signup     - Create account
POST   /api/auth/login      - Login (returns JWT)
GET    /api/auth/me         - Get profile (requires JWT)

Reports:
POST   /api/extraction/upload         - Upload & process PDF
GET    /api/extraction/reports        - List all reports
GET    /api/extraction/reports/:id    - Get report details
DELETE /api/extraction/reports/:id    - Delete report
```

## ⚠️ Troubleshooting

### "Cannot connect to MongoDB"
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### "Python not found"
```bash
# Check if Python is in PATH
where python  # Windows
which python  # Linux/Mac

# Try python3 instead
python3 --version
```

If using python3, edit `Backend/services/agentService.js`:
```javascript
constructor() {
    this.pythonCmd = 'python3';  // Change here
}
```

### "Module not found" error
```bash
# Reinstall dependencies
cd Backend
rm -rf node_modules
npm install
```

### "No PDF files found"
Place your medical report PDFs in `data/pdfs/` directory.

## 📚 What's Next?

- ✅ **Working?** Check [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) for architecture details
- 📖 **API Docs?** See [Backend/README.md](Backend/README.md)
- 🐛 **Issues?** Review console logs, they're very detailed

## 🎉 Success!

If you can upload a PDF and get back summary + recommendations, **you're all set!**

The backend is now:
- ✅ Connected to MongoDB
- ✅ Authenticating users
- ✅ Processing PDFs through all agents
- ✅ Auto-detecting patients
- ✅ Saving complete reports

---

**Happy analyzing! 🔬💊**
