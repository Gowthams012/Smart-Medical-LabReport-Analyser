# Medical Lab Report Chatbot

> AI-powered assistant for analyzing medical lab reports and providing safe, educational health guidance.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/smart-medical-analyser)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🎯 Overview

Medical Lab Report Chatbot is an intelligent assistant that helps users understand their medical lab results through natural conversation. It uses Google's Gemini AI to analyze lab reports and provide educational, evidence-based health guidance while maintaining strict medical safety policies.

### Key Features

✅ **Intelligent Analysis** - AI-powered understanding of various lab report formats  
✅ **Safety First** - Built-in medical guardrails prevent diagnosis and prescriptions  
✅ **Auto Fallback** - Automatic model switching when quota limits are reached  
✅ **Context Aware** - Identifies relevant tests based on your questions  
✅ **Educational** - Provides lifestyle and dietary recommendations  
✅ **Production Ready** - Clean code, error handling, and security best practices

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one free](https://ai.google.dev/))
- Lab report in JSON format

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key (choose one method)
# Method A: Environment variable (Recommended)
export GEMINI_API_KEY="your_api_key_here"    # Linux/Mac
set GEMINI_API_KEY=your_api_key_here         # Windows

# Method B: The script will prompt you if not set
```

### Usage

```bash
# Basic usage
python ChatBot.py path/to/lab_report.json

# Example with relative path
python ChatBot.py "../reports/my_cbc_test.json"

# Example with absolute path
python ChatBot.py "C:\Users\Documents\lab_results.json"
```

---

## 💬 Example Conversations

### Understanding Test Results
```
YOU: What does my hemoglobin level mean?

ASSISTANT:
Your hemoglobin level is 12.5 g/dL, which is slightly below the normal 
range (13.0-17.0 g/dL for men).

**What this means:**
Hemoglobin is the protein in red blood cells that carries oxygen throughout 
your body. A slightly low level may indicate:
• Mild anemia
• Iron or vitamin deficiency
• Dietary factors

**Recommendations:**
• Iron-rich foods: Red meat, spinach, lentils, beans
• Vitamin C foods: Citrus fruits help iron absorption
• Avoid tea/coffee with meals (reduces iron absorption)

⚠️ Consult your doctor to discuss these results and determine the cause.
```

### General Health Questions
```
YOU: What foods can help improve my iron levels?

ASSISTANT:
Great question! Here are excellent iron-rich foods:

**Animal Sources (Heme Iron - Better Absorbed):**
• Red meat (beef, lamb)
• Poultry (chicken, turkey)  
• Fish and seafood
• Liver and organ meats

**Plant Sources (Non-Heme Iron):**
• Spinach and leafy greens
• Lentils and beans
• Fortified cereals
• Pumpkin seeds
• Tofu

**Pro Tips:**
✓ Pair with vitamin C (citrus, bell peppers) for better absorption
✗ Avoid tea/coffee with iron-rich meals

Daily needs: Men 8mg, Women 18mg

Consult a doctor before taking iron supplements.
```

---

## 🛡️ Safety & Medical Policies

### What the Chatbot DOES

✅ Explains lab test results in simple terms  
✅ Provides educational health information  
✅ Suggests lifestyle and dietary improvements  
✅ Offers general nutrition guidance  
✅ Encourages consulting healthcare providers  

### What the Chatbot DOES NOT DO

❌ Diagnose diseases or medical conditions  
❌ Prescribe medications or dosages  
❌ Provide emergency medical advice  
❌ Replace professional medical consultation  
❌ Make treatment recommendations  

### Emergency Detection

If the chatbot detects emergency keywords (chest pain, stroke, severe bleeding), it immediately:
- Stops processing the query
- Directs you to call emergency services
- Does not attempt to provide medical advice

---

## 📊 Supported Lab Report Format

The chatbot works with JSON-formatted lab reports:

```
User Query
   ↓
NLP Layer (Intent Detection + Entity Extraction)
   ↓
Lab Context Builder (Filtered Lab JSON)
   ↓
Medical Guardrails (Safety Rules + Constraints)
   ↓
Gemini LLM (Reasoning Engine)
   ↓
Post-Response Safety Filter
   ↓
User Answer
```

## 🎯 Key Features

### 1. **Enhanced NLP Layer**
- Advanced intent detection (8 categories including nutrition and general medical)
- Intelligent entity extraction with fuzzy matching
- Medical synonym recognition
- Context-aware query understanding

### 2. **Smart Lab Context Builder**
- Filters relevant lab data based on user query
- Highlights abnormal values
- Provides focused context to LLM
- Handles both specific and general queries

### 3. **Medical Guardrails & Policy Enforcement**
- Pre-query validation for safety
- Emergency keyword detection
- Medication request blocking
- Medical ethics compliance
- Evidence-based response guidelines

### 4. **Gemini-Powered Intelligence**
- Uses Gemini 2.5 Flash for fast, accurate responses
- Context-aware prompting
- Educational and supportive tone
- Evidence-based medical information

### 5. **Post-Response Safety Filter**
- Validates LLM output for safety
- Prevents diagnosis language
- Blocks prescription recommendations
- Adds appropriate disclaimers
- Ensures medical policy compliance

### 6. **Medical Knowledge Base** 🆕
- Nutrient sources and benefits
- Lab test interpretations
- Food benefits database
- Lifestyle recommendations
- Evidence-based health information

## 🛡️ Safety Rules

### ✅ **DOES:**
- Explain lab test values in simple language
- Provide educational health information
- Suggest evidence-based lifestyle and dietary improvements
- Offer general nutrition guidance
- Explain food benefits and limitations
- Support and reassure users
- Answer general medical knowledge questions safely
- Encourage consulting healthcare providers

### ❌ **DOES NOT:**
- Diagnose diseases or conditions
- Prescribe medicines, supplements, or dosages
- Provide specific treatment plans
- Handle emergency medical situations
- Make assumptions beyond report data
- Give fear-inducing statements

## 📋 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Gemini API key:**
```bash
# Option 1: Environment variable (Recommended)
set GEMINI_API_KEY=your_api_key_here

# Option 2: Enter when prompted
```

3. **Verify installation:**
```bash
python ChatBotAgent/check_models.py
```

## 🚀 Usage

### Quick Start - Interactive Mode
```bash
python ChatBotAgent/ChatBot.py
```

### Programmatic Usage
```python
from ChatBot import MedicalChatBot

# Initialize
chatbot = MedicalChatBot(
    lab_data_path="path/to/lab_report.json",
    gemini_api_key="your_api_key"
)

# Single query
response = chatbot.chat("What does my hemoglobin level mean?")
print(response)

# Interactive session
chatbot.start_interactive_session()
```

### Run Examples
```bash
python ChatBotAgent/example_usage.py
```

## 💬 Example Conversations

### Lab-Specific Queries
```
User: "My hemoglobin is 12.5 and marked as LOW. What does this mean?"

Bot: Based on your lab results, your hemoglobin level is 12.5 g/dL, which is 
     slightly below the normal range (13.0-17.0 g/dL for men).

     What this means:
     • Hemoglobin carries oxygen in your blood
     • Slightly low levels may indicate:
       - Mild anemia
       - Iron or vitamin deficiency
       - Dietary factors
     
     Lifestyle recommendations:
     • Iron-rich foods: spinach, red meat, lentils, beans
     • Vitamin C helps iron absorption: citrus fruits, tomatoes
     • Avoid tea/coffee with meals (reduces iron absorption)
     
     ⚠️ Please consult with a healthcare provider to discuss these results.
```

### General Health Queries
```
User: "What foods are good sources of iron?"

Bot: Great question! Here are excellent iron-rich foods:

     Animal sources (Heme iron - better absorbed):
     • Red meat (beef, lamb)
     • Poultry (chicken, turkey)
     • Fish and seafood
     • Liver and organ meats
     
     Plant sources (Non-heme iron):
     • Spinach and leafy greens
     • Lentils and beans
     • Fortified cereals
     • Pumpkin seeds
     • Tofu
     
     Tips for better iron absorption:
     ✓ Pair with vitamin C rich foods (citrus, bell peppers)
     ✗ Avoid tea/coffee with meals
     
     Daily needs: Men 8mg, Women 18mg (pre-menopause)
     
     📋 This is general nutrition information. Your specific needs may vary.
```

### Nutrition & Food Benefits
```
User: "What are the benefits of eating bananas?"

Bot: Bananas are nutritious fruits with several health benefits:

     Key nutrients:
     • Potassium: Heart health, blood pressure regulation
     • Vitamin B6: Brain function, metabolism
     • Fiber: Digestive health
     • Vitamin C: Immune support
     
     Health benefits:
     • Supports healthy blood pressure
     • Quick energy source for exercise
     • May improve mood (contains tryptophan)
     • Aids digestion
     
     Considerations:
     ⚠️ Moderate natural sugar content
     ⚠️ People with diabetes should portion control
     ⚠️ Those on certain medications should consult doctor
     
     General recommendation: 1-2 bananas per day as part of balanced diet
```

## 🎭 Query Types Supported

| Category | Examples | Bot Response |
|----------|----------|--------------|
| **Lab Value Interpretation** | "What does my PCV of 40% mean?" | Explains value with context from report |
| **Test Explanation** | "What is hemoglobin?" | Educational explanation + your values |
| **Health Advice** | "How can I improve my iron levels?" | Evidence-based lifestyle tips |
| **Nutrition** | "What foods help with cholesterol?" | Food sources + benefits + cautions |
| **Comparison** | "What's the difference between HDL and LDL?" | Clear comparison with examples |
| **General Medical** | "Why is vitamin D important?" | Educational info with safety |

## 🚫 Blocked Queries (Safety)

**Medication Requests:**
```
User: "What medicine should I take for low hemoglobin?"
Bot:  💊 I cannot prescribe medications. Please consult your healthcare provider.
```

**Diagnosis Requests:**
```
User: "Do I have diabetes?"
Bot:  I cannot diagnose medical conditions. Please see a doctor for diagnosis.
```

**Emergency Situations:**
```
User: "I'm having severe chest pain, what should I do?"
Bot:  🚨 For emergency medical situations, please seek immediate medical attention.
```

## 🔧 Configuration

### Update Lab Report Path
Edit in `ChatBot.py`:
```python
LAB_REPORT_PATH = r"path\to\your\lab_report.json"
```

### Change Gemini Model
Edit in `ChatBot.py`:
```python
self.model = genai.GenerativeModel('gemini-2.5-flash')  # Current
# Or: 'gemini-1.5-pro-latest', 'gemini-1.5-flash-latest'
```

### Customize Safety Rules
Edit `MedicalGuardrails` class in `ChatBot.py`

## 📊 Supported Lab Report Format

```json
{
  "report_type": "medical_lab_report",
  "patient": {
    "demographics": {},
    "identifiers": {"sample_type": "Blood"}
  },
  "test_results": [
    {
      "test_name": "Hemoglobin (Hb)",
      "result_value": 12.5,
      "result_text": "12.5",
      "abnormal": false,
      "unit": "g/dL",
      "reference_range": {
        "min": 13.0,
        "max": 17.0,
        "text": "g/dL"
      },
      "flag": "LOW"  // Optional: HIGH, LOW, CRITICAL
    }
  ]
}
```

## 🧪 Debug Mode

Enable verbose logging to see the AI's reasoning:
```
[NLP] Intent: value_interpretation
[NLP] Entities: ['hemoglobin']
[CONTEXT] Found 1 relevant tests
[CONTEXT] Abnormal values: 1
[LLM] Generating response...
[FILTER] Safety check: PASS
```

## 📈 Performance

- **Response Time:** ~2-4 seconds (Gemini 2.5 Flash)
- **Accuracy:** High (context-aware + medical knowledge base)
- **Safety:** Multi-layer filtering + policy enforcement
- **Scalability:** Handles multiple lab reports and concurrent users

## 🧠 Medical Intelligence Features

1. **Nutrient Database:** 50+ nutrients with food sources
2. **Lab Test Info:** Normal ranges, interpretations, lifestyle tips
3. **Food Benefits:** Evidence-based food information
4. **Synonym Recognition:** Understands medical terminology variations
5. **Context Awareness:** Relates general questions to user's lab data

## ⚠️ Important Disclaimers

1. **Not a Medical Device:** This is an educational tool, not approved for medical diagnosis
2. **No Doctor Replacement:** Always consult healthcare providers for medical decisions
3. **Emergency:** Seek immediate help for emergencies, don't rely on chatbot
4. **Data Privacy:** Lab data processed locally, review API privacy policies
5. **Accuracy:** While evidence-based, information may not cover all cases

## 🤝 Contributing

To enhance medical intelligence:
1. Add entries to `medical_knowledge.py`
2. Update `LAB_TEST_ENTITIES` in `NLPLayer`
3. Enhance safety rules in `MedicalGuardrails`
4. Test with diverse queries

## 📝 License

Part of the Smart Medical Analyser system.

## 🆘 Support

For issues:
1. Check API key is valid
2. Verify lab report JSON format
3. Review error messages in debug output
4. Ensure internet connection for Gemini API

---

**Built with:** Python 3.8+, Google Gemini AI, Medical Evidence-Based Guidelines

**Last Updated:** January 26, 2026
