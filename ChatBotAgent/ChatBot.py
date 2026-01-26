"""
Medical Lab Report Chatbot
===========================
An AI-powered chatbot for analyzing medical lab reports and providing 
safe, educational health guidance.

Author: Smart Medical Analyser Team
Version: 1.0.0
License: MIT
"""

import os
import json
import sys
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION ---
class Config:
    """Application configuration"""
    # API Key - Priority: Environment Variable > Config File > Manual Input
    API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Model fallback list (ordered by preference)
    # Models confirmed working with google.generativeai library
    MODELS = [
        'gemini-2.5-flash',           # Latest, most capable
        'gemini-flash-latest',        # Alias to latest stable
        'gemini-2.0-flash-lite',      # Lighter weight, better quota
        'gemini-2.5-flash-lite',      # Alternative lite version
    ]
    
    # Application settings
    DEBUG = True  # Enable to see model switching logs
    MAX_CHAT_HISTORY = 10

class MedicalSafetyLayer:
    """
    STRICT POLICY ENFORCEMENT
    Ensures the bot never crosses the line into illegal medical practice.
    """
    
    EMERGENCY_KEYWORDS = [
        "chest pain", "heart attack", "stroke", "can't breathe", 
        "unconscious", "bleeding heavily", "suicide", "kill myself",
        "emergency", "collapse", "seizure"
    ]
    
    PROHIBITED_INTENTS = [
        "prescribe", "medication name", "dosage", "what drug", 
        "diagnose me", "do i have cancer"
    ]

    @staticmethod
    def is_emergency(query: str) -> bool:
        """Checks for life-threatening keywords."""
        return any(k in query.lower() for k in MedicalSafetyLayer.EMERGENCY_KEYWORDS)

    @staticmethod
    def is_unethical(query: str) -> bool:
        """Checks for prescription/diagnosis requests."""
        return any(k in query.lower() for k in MedicalSafetyLayer.PROHIBITED_INTENTS)

class MedicalReasoningEngine:
    """
    AI-powered medical reasoning engine with automatic model fallback.
    Handles quota limits gracefully by trying multiple models.
    """
    
    def __init__(self, api_key):
        """Initialize the reasoning engine with API credentials"""
        genai.configure(api_key=api_key)
        self.model_name = Config.MODELS[0]
        self.current_model_index = 0
        if Config.DEBUG:
            print(f"🤖 Using model: {self.model_name}")
    
    def _call_with_fallback(self, prompt: str, operation_name: str = "API call"):
        """
        Execute API call with automatic model fallback on quota errors.
        
        Args:
            prompt: The prompt to send to the model
            operation_name: Description of the operation (for logging)
            
        Returns:
            API response object
            
        Raises:
            Exception: If all models fail or non-quota error occurs
        """
        last_error = None
        
        for attempt, model in enumerate(Config.MODELS[self.current_model_index:], start=1):
            try:
                print(f"🔄 Attempt {attempt}: Trying model '{model}' for {operation_name}...", file=sys.stderr)
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
                
                # Success! Update current model if switched
                if model != self.model_name:
                    self.model_name = model
                    self.current_model_index = Config.MODELS.index(model)
                    print(f"✅ Switched to model: {self.model_name}", file=sys.stderr)
                else:
                    print(f"✅ Using model: {self.model_name}", file=sys.stderr)
                
                return response
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Check if quota/rate limit error
                is_quota_error = any(keyword in error_str.lower() for keyword in [
                    '429', 'resource_exhausted', 'quota', 'rate limit', 'too many requests'
                ])
                
                if is_quota_error:
                    print(f"⚠️  Model '{model}' quota exceeded: {error_str[:100]}...", file=sys.stderr)
                    
                    # Check if more models available
                    remaining = len(Config.MODELS) - self.current_model_index - attempt
                    if remaining > 0:
                        print(f"🔄 {remaining} backup model(s) available. Retrying...", file=sys.stderr)
                        continue
                    else:
                        # Last model also failed
                        print(f"❌ All {len(Config.MODELS)} models exhausted quota!", file=sys.stderr)
                        raise Exception(
                            f"All models hit rate limits. Tried: {', '.join(Config.MODELS)}\n"
                            f"Solutions:\n"
                            f"  1. Wait 1-2 minutes for free tier quota reset\n"
                            f"  2. Get new API key from: https://aistudio.google.com/apikey\n"
                            f"  3. Upgrade to paid plan for unlimited quota"
                        )
                else:
                    # Non-quota error - raise immediately with context
                    print(f"❌ Model '{model}' error (non-quota): {error_str[:200]}", file=sys.stderr)
                    raise Exception(f"Model {model} failed: {error_str}")
        
        raise Exception(f"No models available. Last error: {last_error}")

    def identify_relevant_tests(self, user_query: str, all_test_names: list) -> list:
        """
        Identify relevant tests from lab report based on user query.
        
        Args:
            user_query: User's question
            all_test_names: List of all available test names
            
        Returns:
            List of relevant test names
        """
        prompt = f"""
        ACT AS: Medical Data Selector.
        
        TASK:
        The user asked: "{user_query}"
        The available tests in their report are: {json.dumps(all_test_names)}
        
        INSTRUCTION:
        Return a JSON list of ONLY the test names from the provided list that are relevant to the user's question.
        If the user asks "How is my health?", return ALL test names.
        If the user asks "Is my liver okay?", return only liver-related tests (e.g., ALT, AST, Bilirubin).
        
        OUTPUT FORMAT: JSON List of strings ONLY. No markdown.
        """
        try:
            response = self._call_with_fallback(prompt, "test identification")
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            if Config.DEBUG:
                print(f"⚠️  AI selection failed: {e}")
            # Fallback: keyword matching
            return [t for t in all_test_names if any(word.lower() in user_query.lower() for word in t.split())]

    def generate_medical_response(self, user_query: str, relevant_data: list, full_history: list) -> str:
        """
        Generates safe, personalized medical response with all required behaviors.
        
        ✔ Lab-aware answers
        ✔ Risk indicator  
        ✔ Personalized food advice
        ✔ Simple explanations
        ✔ Safety guardrails
        """
        # Medical Guidelines System Prompt
        system_prompt = f"""
        You are 'MediBot', a Clinical Decision Support AI specialized in lab report analysis.
        
        YOUR CORE BEHAVIORS (STRICTLY FOLLOW):
        
        ✔ LAB-AWARE ANSWERS:
        - Always reference the user's actual lab values in your response
        - Compare their values to normal ranges
        - Explain if values are normal, borderline, or abnormal
        - Use phrases like "Based on YOUR lab results..." or "Looking at YOUR [test name]..."
        
        ✔ RISK INDICATORS:
        - Clearly indicate risk levels: 🟢 Normal | 🟡 Borderline | 🔴 Abnormal
        - Explain what each abnormal value could indicate (not diagnose!)
        - Use phrases: "may indicate", "could suggest", "is associated with"
        - Never say "You have [disease]" - say "Your results indicate elevated risk of..."
        
        ✔ PERSONALIZED FOOD ADVICE:
        - Provide specific foods tailored to their abnormal values
        - Include portions/frequency when safe (e.g., "1-2 servings daily")
        - List foods to INCREASE and foods to LIMIT/AVOID
        - Explain HOW the food helps (e.g., "Spinach is rich in iron which helps increase hemoglobin")
        - Give practical meal ideas or combinations
        
        ✔ SIMPLE EXPLANATIONS:
        - Use plain language, avoid medical jargon
        - If technical terms needed, explain them in parentheses
        - Use analogies when helpful (e.g., "Hemoglobin is like delivery trucks for oxygen")
        - Break complex info into bullet points
        - Keep sentences short and clear
        
        ✔ SAFETY GUARDRAILS:
        - NEVER diagnose diseases ("You have diabetes" ❌)
        - NEVER prescribe medications or dosages
        - NEVER give emergency medical advice (redirect to 911)
        - ALWAYS end with "Consult your doctor for personalized medical advice"
        - Use risk language: "may indicate", "could suggest", "is associated with"
        
        STRICT MEDICAL POLICIES:
        1. **No Diagnosis:** Say "Your results indicate a risk of..." NOT "You have [Disease]"
        2. **No Prescriptions:** Never suggest medication names or dosages
        3. **Holistic Approach:** Connect related results (e.g., low Iron + low Hemoglobin)
        4. **Actionable Advice:** Only lifestyle and dietary interventions
        5. **Always Personalized:** Reference their specific lab values
        
        USER'S LAB RESULTS:
        {json.dumps(relevant_data, indent=2)}

        CHAT HISTORY (Context):
        {full_history[-3:] if full_history else "First message"}

        USER QUESTION: "{user_query}"
        
        RESPONSE STRUCTURE (Follow this format):
        
        1. **LAB-AWARE OPENING** 
           - Reference their specific values with risk indicators
           - Example: "🟡 Your hemoglobin is 12.5 g/dL, which is slightly below normal (13-17 g/dL)."
        
        2. **WHAT THIS MEANS** (Simple explanation)
           - Explain in plain language
           - Example: "Hemoglobin carries oxygen in your blood. Low levels mean less oxygen delivery."
        
        3. **RISK INDICATOR**
           - What this could indicate (not diagnose!)
           - Example: "This may indicate iron deficiency or mild anemia."
        
        4. **PERSONALIZED FOOD ADVICE**
           Foods to INCREASE:
           • [Specific food] - [why it helps] - [how much]
           • [Specific food] - [why it helps] - [how much]
           
           Foods to LIMIT:
           • [Food] - [reason]
        
        5. **LIFESTYLE TIPS** (if applicable)
           - Specific, actionable recommendations
        
        6. **DISCLAIMER** (Always end with this)
           "⚠️ Please consult your doctor to discuss these results and get personalized medical advice."
        
        GENERATE RESPONSE NOW:
        """
        
        response = self._call_with_fallback(system_prompt, "response generation")
        return response.text

class UniversalLabChatbot:
    """
    Main chatbot class for analyzing medical lab reports.
    """
    
    def __init__(self, json_path: str):
        """
        Initialize chatbot with lab report data.
        
        Args:
            json_path: Path to lab report JSON file
        """
        # Get API key
        self.api_key = Config.API_KEY
        if not self.api_key:
            print("\n❌ Error: GEMINI_API_KEY not found!")
            print("\nPlease set your API key using one of these methods:")
            print("  1. Environment variable: set GEMINI_API_KEY=your_key_here")
            print("  2. Manual input: Enter when prompted below\n")
            self.api_key = input("Enter your Gemini API key: ").strip()
            if not self.api_key:
                print("❌ No API key provided. Exiting.")
                sys.exit(1)
            
        self.engine = MedicalReasoningEngine(self.api_key)
        self.lab_data = self._load_lab_report(json_path)
        self.chat_history = []
        
        # Extract test names from report
        self.flat_tests = self._extract_test_names(self.lab_data)
        print(f"✅ Loaded {len(self.flat_tests)} tests from report.")

    def _load_lab_report(self, path: str) -> dict:
        """Load and validate lab report JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"❌ Error: File not found at {path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            sys.exit(1)

    def _extract_test_names(self, data) -> list:
        """
        Recursively extract test names from lab report.
        Handles various JSON structures (FHIR, custom formats, etc.)
        """
        names = []
        if isinstance(data, dict):
            for k, v in data.items():
                if k == "test_name" and v:
                    names.append(v)
                elif k == "tests" and isinstance(v, list):
                    for item in v:
                        names.extend(self._extract_test_names(item))
                else:
                    names.extend(self._extract_test_names(v))
        elif isinstance(data, list):
            for item in data:
                names.extend(self._extract_test_names(item))
        return list(set(filter(None, names)))  # Remove None values and duplicates

    def _get_test_data(self, test_names: list) -> list:
        """
        Retrieve full test data for selected test names.
        
        Args:
            test_names: List of test names to retrieve
            
        Returns:
            List of test data objects
        """
        results = []
        
        def find_test(data, target_names):
            """Recursive search for test data"""
            if isinstance(data, dict):
                if "test_name" in data and data["test_name"] in target_names:
                    results.append(data)
                for v in data.values():
                    find_test(v, target_names)
            elif isinstance(data, list):
                for item in data:
                    find_test(item, target_names)
        
        find_test(self.lab_data, test_names)
        return results

    def chat(self, user_query: str) -> str:
        """
        Process user query and generate response.
        
        Args:
            user_query: User's question about lab results
            
        Returns:
            AI-generated response
        """
        # Safety checks
        if MedicalSafetyLayer.is_emergency(user_query):
            return ("🚨 **EMERGENCY DETECTED**\n\n"
                   "This sounds like a medical emergency. Please:\n"
                   "• Call emergency services (911/112) immediately\n"
                   "• Seek immediate medical attention\n"
                   "• Do not rely on this chatbot for emergency situations")
        
        if MedicalSafetyLayer.is_unethical(user_query):
            return ("⚠️ **POLICY RESTRICTION**\n\n"
                   "I cannot:\n"
                   "• Provide medical diagnoses\n"
                   "• Prescribe medications or dosages\n"
                   "• Replace professional medical advice\n\n"
                   "I can:\n"
                   "• Explain your lab test results\n"
                   "• Suggest lifestyle and dietary changes\n"
                   "• Provide educational health information\n\n"
                   "Please consult a healthcare provider for medical decisions.")

        # Identify relevant tests
        print("🤔 Analyzing report for relevant data...", end="\r")
        relevant_test_names = self.engine.identify_relevant_tests(user_query, self.flat_tests)
        
        # Retrieve test data
        relevant_data = self._get_test_data(relevant_test_names)
        
        # Fallback for general queries
        if not relevant_data and any(word in user_query.lower() for word in ['summary', 'overall', 'everything', 'all']):
            relevant_data = self.lab_data
        
        # Generate response
        print("💡 Formulating medical insights...", end="\r")
        response = self.engine.generate_medical_response(user_query, relevant_data, self.chat_history)
        
        # Update chat history (keep last N exchanges)
        self.chat_history.append(f"User: {user_query}")
        self.chat_history.append(f"Bot: {response}")
        if len(self.chat_history) > Config.MAX_CHAT_HISTORY:
            self.chat_history = self.chat_history[-Config.MAX_CHAT_HISTORY:]
        
        return response

# --- MAIN EXECUTION ---
def main():
    """Main application entry point"""
    print("="*60)
    print("🩺 MEDICAL LAB REPORT CHATBOT")
    print("   AI-Powered Health Analysis Assistant")
    print("="*60)
    print("\n✨ INTELLIGENT FEATURES:")
    print("   ✔ Lab-aware answers")
    print("   ✔ Risk indicators (🟢 🟡 🔴)")
    print("   ✔ Personalized food advice")
    print("   ✔ Simple explanations")
    print("   ✔ Safety guardrails")
    print("="*60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\n❌ Error: No lab report file provided\n")
        print("Usage:")
        print("  python ChatBot.py <path_to_lab_report.json>\n")
        print("Example:")
        print("  python ChatBot.py reports/my_lab_report.json")
        print("  python ChatBot.py \"C:\\Users\\Documents\\report.json\"\n")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    # Resolve path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    # Validate file exists
    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found!")
        print(f"   Path: {file_path}")
        print(f"   Current directory: {os.getcwd()}\n")
        sys.exit(1)

    # Initialize chatbot
    try:
        bot = UniversalLabChatbot(file_path)
    except Exception as e:
        print(f"\n❌ Failed to initialize chatbot: {e}\n")
        sys.exit(1)
    
    # Start interactive session
    print("\n💬 Chat session started. Type 'exit' to quit.")
    print("   Ask questions about your lab results!\n")
    
    while True:
        try:
            user_input = input("YOU: ").strip()
            
            # Exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Thank you for using Medical Lab Chatbot. Stay healthy!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Help command
            if user_input.lower() in ['help', '?']:
                print("\n📋 Example questions you can ask:")
                print("  • What does my hemoglobin level mean?")
                print("  • Are my liver function tests normal?")
                print("  • Give me a summary of all my results")
                print("  • What foods can improve my iron levels?")
                print("  • Is my cholesterol high?\n")
                continue
                
            # Process query
            reply = bot.chat(user_input)
            print(f"\n🤖 ASSISTANT:\n{reply}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()