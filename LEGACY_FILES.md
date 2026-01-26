# Legacy Files - Not Used in Production

## main.py
**Status**: ⚠️ Legacy - Not used in production

**Purpose**: Original Python-based workflow for testing agents without Node.js backend

**Replaced By**: Node.js Backend (`Backend/server.js` + `Backend/services/agentService.js`)

**Why Not Used**:
- No user authentication
- No database integration
- No REST API
- No multi-user support
- Command-line only

**Keep For**: Development testing of Python agents in isolation

---

## When to Use Legacy Files

### Use main.py When:
- Testing individual agents without full backend
- Debugging Python agent logic
- Quick prototyping of new agent features
- Running agents standalone for development

### Example Usage:
```bash
python main.py
```

This will run the complete Python-only workflow:
1. Extract data from sample PDF
2. Generate summary using Gemini
3. Generate recommendations using Gemini
4. Segregate PDF into patient vault

---

## Production System

Use the Node.js backend for all production operations:
```bash
cd Backend
npm run dev
```

The backend provides:
- ✅ User authentication & authorization
- ✅ MongoDB database integration
- ✅ REST API endpoints
- ✅ Multi-user support
- ✅ Secure file uploads
- ✅ JWT token management
- ✅ Error handling & logging

---

## Migration Notes

If you need to add features:
1. **Agent Logic**: Update Python files in respective agent folders
2. **API Integration**: Update `Backend/services/agentService.js`
3. **Database Models**: Update files in `Backend/Database/Models/`
4. **API Routes**: Update `Backend/routes/` and `Backend/controllers/`

Never modify `main.py` for production features.
