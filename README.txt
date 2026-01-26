SMART MEDICAL ANALYSER
======================

Complete Integrated Medical Lab Report Processing System

STRUCTURE:
----------
Smart-Medical-Analyser/
├── main.py                    # Main integrated workflow
├── data/pdfs/                # Input PDFs folder
├── integrated_output/        # All outputs (extraction + vault)
│
├── ChatBotAgent/             # Medical Q&A Chatbot
│   ├── ChatBot.py
│   └── requirements.txt
│
├── ExtractionAgent/          # PDF Extraction & Structuring
│   ├── ExtractionAgent.py   # Main pipeline
│   ├── pdf_extraction.py    # PDF to text/CSV
│   └── data_structuring.py  # CSV to JSON
│
├── InsightAgent/             # Clinical Analysis
│   ├── Summary.py           # Generate medical summaries
│   └── Recommendation.py    # Generate recommendations (Dos/Don'ts/Foods)
│
└── ValutAgent/              # Patient Vault Management
    ├── ValutAgent.py        # Smart patient segregation
    └── requirements.txt

USAGE:
------
1. Run Complete Workflow:
   python main.py "data/pdfs/your_report.pdf"

2. Run Individual Agents:
   - Chatbot: python ChatBotAgent/ChatBot.py "path/to/json"
   - Summary: python InsightAgent/Summary.py "path/to/json"
   - Recommendations: python InsightAgent/Recommendation.py "path/to/json"

OUTPUT STRUCTURE:
-----------------
integrated_output/
└── PatientVaults/
    └── patient_name/
        └── report.pdf         # Only original PDF stored

FEATURES:
---------
✓ PDF Extraction (Text, Tables, JSON)
✓ Clinical Summary Generation
✓ Medical Recommendations (Dos/Don'ts/Foods)
✓ Smart Patient-Based Vault Segregation
✓ Interactive Medical Chatbot (Lab-aware)

API KEY:
--------
Set GOOGLE_API_KEY environment variable or update in agent files
