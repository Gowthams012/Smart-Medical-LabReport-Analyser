# System Architecture Diagram

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Postman/Frontend)                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         NODE.JS EXPRESS SERVER                           │
│                              (Port 5000)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐  │
│  │  Auth Routes    │     │ Extraction      │     │  Other Routes    │  │
│  │  /api/auth/*    │     │ Routes          │     │  (Future)        │  │
│  │                 │     │ /api/extraction │     │                  │  │
│  └────────┬────────┘     └────────┬────────┘     └──────────────────┘  │
│           │                       │                                      │
│           ▼                       ▼                                      │
│  ┌─────────────────┐     ┌─────────────────────────────────────────┐  │
│  │ Auth Controller │     │  Extraction Controller                  │  │
│  │ - signup        │     │  - uploadReport (main pipeline)        │  │
│  │ - login         │     │  - getMyReports                        │  │
│  │ - getMe         │     │  - getReportById                       │  │
│  └────────┬────────┘     └────────┬────────────────────────────────┘  │
│           │                       │                                      │
│           │                       │ Uses                                 │
│           │                       ▼                                      │
│           │              ┌─────────────────────────────────────────┐   │
│           │              │     Agent Service                       │   │
│           │              │  (Python Integration Layer)            │   │
│           │              │  - processWithVaultAgent()            │   │
│           │              │  - extractData()                      │   │
│           │              │  - generateSummary()                  │   │
│           │              │  - generateRecommendations()          │   │
│           │              │  - processComplete()                  │   │
│           │              └────────┬───────────────────────────────┘   │
│           │                       │                                      │
└───────────┼───────────────────────┼──────────────────────────────────────┘
            │                       │
            │                       │ spawn('python', ...)
            │                       ▼
            │              ┌─────────────────────────────────────────────┐
            │              │         PYTHON AGENTS (CLI)                 │
            │              ├─────────────────────────────────────────────┤
            │              │                                             │
            │              │  ┌────────────────────────────────────┐   │
            │              │  │  VaultAgent                        │   │
            │              │  │  Input: PDF path                   │   │
            │              │  │  Output: Patient name, vault path  │   │
            │              │  │  Files: PatientVaults/{name}/      │   │
            │              │  └────────────────────────────────────┘   │
            │              │           │                                 │
            │              │           ▼                                 │
            │              │  ┌────────────────────────────────────┐   │
            │              │  │  ExtractionAgent                   │   │
            │              │  │  Input: PDF path                   │   │
            │              │  │  Output: Medical data JSON         │   │
            │              │  │  Files: extractions/{id}/json/     │   │
            │              │  └────────────────────────────────────┘   │
            │              │           │                                 │
            │              │           ▼                                 │
            │              │  ┌──────────────────┬─────────────────┐   │
            │              │  │                  │                 │   │
            │              │  ▼                  ▼                 │   │
            │              │  ┌──────────────┐  ┌──────────────┐  │   │
            │              │  │ SummaryAgent │  │Recommendation│  │   │
            │              │  │              │  │    Agent     │  │   │
            │              │  │ Input: JSON  │  │ Input: JSON  │  │   │
            │              │  │ Output: TXT  │  │ Output: MD   │  │   │
            │              │  │ Files:       │  │ Files:       │  │   │
            │              │  │ summary_     │  │ medical_     │  │   │
            │              │  │ output/      │  │ recommen.../ │  │   │
            │              │  └──────────────┘  └──────────────┘  │   │
            │              │         (Parallel Execution)          │   │
            │              └─────────────────────────────────────────────┘
            │                       │
            │                       │ Read output files
            │                       ▼
            │              ┌─────────────────────────────────────────────┐
            │              │     Aggregated Results                      │
            │              │  - patientName                              │
            │              │  - extractedData (JSON)                     │
            │              │  - summary (text)                           │
            │              │  - recommendations (markdown)               │
            │              └────────┬────────────────────────────────────┘
            │                       │
            ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            MONGODB DATABASE                              │
│                      mongodb://localhost:27017                           │
│                    Database: Smart-Lab-Analyser                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ user         │  │ report       │  │ vault        │  │ chatbot    │ │
│  │ collection   │  │ collection   │  │ collection   │  │ collection │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤ │
│  │ - email      │  │ - userID     │  │ - userID     │  │ - userID   │ │
│  │ - username   │  │ - patientName│  │ - files[]    │  │ - history  │ │
│  │ - password   │  │ - reportType │  │   • fileName │  │   (future) │ │
│  │ - googleId   │  │ - extracted  │  │   • fileURL  │  │            │ │
│  │              │  │   Data       │  │   • reportId │  │            │ │
│  │              │  │ - summary    │  │   • status   │  │            │ │
│  │              │  │ - recommen   │  │              │  │            │ │
│  │              │  │   dations    │  │              │  │            │ │
│  │              │  │ - riskLevel  │  │              │  │            │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│         ▲                 ▲                  ▲                          │
│         │                 │                  │                          │
│         └─────────────────┴──────────────────┘                          │
│                    References via ObjectId                              │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Middleware Flow

```
Client Request
     │
     ▼
┌─────────────────┐
│ CORS Middleware │  ← Allow cross-origin requests
└────────┬────────┘
         ▼
┌─────────────────┐
│ Body Parser     │  ← Parse JSON/form-data
└────────┬────────┘
         ▼
┌─────────────────┐
│ Auth Middleware │  ← Verify JWT token (if protected route)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Multer Upload   │  ← Handle file upload (if file route)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Controller      │  ← Handle business logic
└────────┬────────┘
         ▼
┌─────────────────┐
│ Service Layer   │  ← Agent integration, DB operations
└────────┬────────┘
         ▼
   Response to Client
```

## File Storage Structure

```
Smart-Medical-Analyser/
│
├── Backend/
│   ├── uploads/                    ← User uploaded files
│   │   └── {userId}/
│   │       └── timestamp_filename.pdf
│   │
│   ├── services/
│   │   └── agentService.js        ← Python integration
│   │
│   ├── controllers/
│   │   ├── authController.js      ← Auth logic
│   │   └── extractionController.js ← Report logic
│   │
│   └── Database/
│       └── Models/                 ← Mongoose schemas
│
├── integrated_output/              ← Agent outputs
│   ├── extractions/
│   │   └── {session}/
│   │       └── json/
│   │           └── {id}_medical_report.json
│   │
│   └── PatientVaults/
│       └── {patientName}/
│           └── {filename}.pdf
│
├── summary_output/                 ← Clinical summaries
│   └── {id}_summary_{timestamp}.txt
│
└── medical_recommendations/        ← Medical protocols
    └── PROTOCOL_{id}_{timestamp}.md
```

## Data Flow Timeline

```
t=0s    User uploads PDF
         ↓
t=1s    File saved to Backend/uploads/{userId}/
         ↓
t=2s    VaultAgent starts
         ↓
t=4s    Patient identified, PDF copied to PatientVaults/
         ↓
t=5s    ExtractionAgent starts
         ↓
t=18s   Medical data extracted, JSON saved
         ↓
t=19s   SummaryAgent & RecommendationAgent start (parallel)
         ↓
t=25s   Both agents complete, files saved
         ↓
t=26s   All results aggregated
         ↓
t=27s   Report saved to MongoDB
         ↓
t=28s   Vault updated with file metadata
         ↓
t=29s   Response sent to client
```

## Authentication Flow

```
┌──────────┐                 ┌──────────┐                ┌──────────┐
│  Client  │                 │  Server  │                │ MongoDB  │
└────┬─────┘                 └─────┬────┘                └────┬─────┘
     │                             │                          │
     │  POST /auth/signup          │                          │
     │ (email, password)           │                          │
     ├────────────────────────────>│                          │
     │                             │  Hash password           │
     │                             │  (bcrypt)                │
     │                             │                          │
     │                             │  Save user               │
     │                             ├─────────────────────────>│
     │                             │                          │
     │                             │<─────────────────────────┤
     │                             │  User created            │
     │                             │                          │
     │                             │  Generate JWT            │
     │                             │  (jsonwebtoken)          │
     │                             │                          │
     │<────────────────────────────┤                          │
     │  { token, user }            │                          │
     │                             │                          │
     │                             │                          │
     │  POST /extraction/upload    │                          │
     │  Header: Bearer {token}     │                          │
     ├────────────────────────────>│                          │
     │                             │  Verify token            │
     │                             │  Extract user ID         │
     │                             │                          │
     │                             │  Get user                │
     │                             ├─────────────────────────>│
     │                             │<─────────────────────────┤
     │                             │  User data               │
     │                             │                          │
     │                             │  Process request         │
     │                             │  (authenticated)         │
     │                             │                          │
     │<────────────────────────────┤                          │
     │  Response                   │                          │
```

## Error Handling Flow

```
Agent Execution
     │
     ├─── Success ────┐
     │                │
     │                ▼
     │         Read output files
     │                │
     │                ▼
     │         Parse & validate
     │                │
     │                ▼
     │         Return to controller
     │
     └─── Failure ────┐
                      │
                      ▼
              Log detailed error
                      │
                      ▼
              Throw descriptive error
                      │
                      ▼
              Controller catches
                      │
                      ▼
              Return 500 response
                      │
                      ▼
              Client receives error
```

---

**This architecture ensures:**
- ✅ Clean separation of concerns
- ✅ No modification of Python agents
- ✅ File-based communication
- ✅ Scalable design
- ✅ Easy debugging
- ✅ Maintainable codebase
