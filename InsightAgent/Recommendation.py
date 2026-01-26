import sys
import json
import os
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
# Get API Key from environment variable (passed from Node.js or set in .env)
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_GEMINI_API_KEY environment variable not set")
    sys.exit(1)

OUTPUT_FOLDER = "medical_recommendations"

# List of models to try in order (fallback system)
MODELS_TO_TRY = [
    'gemini-2.5-flash',           # Latest, most capable
    'gemini-flash-latest',        # Alias to latest stable
    'gemini-2.0-flash-lite',      # Lighter weight, better quota
    'gemini-2.5-flash-lite',      # Alternative lite version
]

def get_medical_recommendations(json_data):
    """
    Sends lab data to Gemini with a 'Clinical Decision Support' persona.
    Focuses on Dos, Don'ts, and Specific Food Interventions.
    """
    if not api_key:
        return "❌ Error: API Key is missing. Please set GOOGLE_API_KEY environment variable."

    genai.configure(api_key=api_key)
    
    # Try each model in sequence
    for model_name in MODELS_TO_TRY:
        try:
            print(f"🔄 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)

            # --- THE PROMPT: CLINICAL INTELLIGENCE & DIET STRATEGY ---
            prompt = f"""
            You are 'MedRecAgent', a highly advanced Clinical Decision Support System.
            
            YOUR GOAL: 
            Analyze the patient's lab report and generate a **strict, safety-focused Action Protocol**.
            
            CRITICAL INSTRUCTION: 
            You must be highly specific. Do not just say "eat healthy." 
            You must recommend specific foods that chemically interact with the patient's specific abnormal markers.

            INPUT LAB DATA:
            {json.dumps(json_data, indent=2)}

            --- OUTPUT STRUCTURE (Use Markdown) ---

            ## 🏥 Clinical Status Snapshot
            (1 bullet point summarizing the primary concern. e.g., "Patient indicates pre-diabetic markers with elevated liver enzymes.")

            ## 📋 The Protocol: Immediate Actions
            
            ### ✅ WHAT TO DO (Protective Actions)
            *List 3 specific, science-backed lifestyle/supplement interventions.*
            * **Lifestyle:** (e.g., "Implement 'Zone 2' cardio training to assist with lipid oxidation.")
            * **Supplementation:** (e.g., "Consider Vitamin D3 + K2 due to low levels.")

            ### ⛔ WHAT TO AVOID (Contraindications)
            *This is CRITICAL. Tell them what behaviors/foods will spike their bad numbers.*
            * **Dietary Hazards:** (e.g., "Strictly limit fructose and alcohol as your Uric Acid is elevated.")
            * **Lifestyle Risks:** (e.g., "Avoid high-intensity lifting until blood pressure stabilizes.")

            ## 🥗 Top Food Recommendations (Personalized)
            *Based on your specific blood markers, incorporate these 5 Superfoods into your diet this week:*
            
            1. **[Specific Food Item]**: (Why? e.g., "Rich in Omega-3s to lower your high Triglycerides.")
            2. **[Specific Food Item]**: (Why? e.g., "Contains nitrates to help lower your Blood Pressure.")
            3. **[Specific Food Item]**: (Why? e.g., "High in soluble fiber to bind to your excess LDL Cholesterol.")
            4. **[Specific Food Item]**: (Why?)
            5. **[Specific Food Item]**: (Why?)

            ## 🔬 Deep Medical Intelligence (Correlations)
            *Explain ONE hidden connection in their data.*
            (e.g., "Your High TSH combined with High Cholesterol is a classic pattern. Treating the Thyroid often lowers the Cholesterol automatically.")

            ## 🩺 Next Clinical Steps
            * "Re-test [Test Name] in [Number] weeks."
            * "Schedule appointment with [Specialist Type]."

            ---
            **DISCLAIMER:** *I am an AI Recommendation Agent, not a doctor. This report is for educational purposes and should be reviewed by a certified medical professional before starting any new treatment.*
            """

            response = model.generate_content(prompt)
            print(f"✅ Successfully used model: {model_name}")
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️  Quota exceeded for {model_name}, trying next model...")
                continue 
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"⚠️  Model {model_name} not available, trying next...")
                continue 
            else:
                return f"Error connecting to AI ({model_name}): {str(e)}"
    
    return "❌ All Gemini models exceeded quota or unavailable. Please try again later."

def main(file_path=None):
    """
    Main function to generate medical recommendations.
    Returns the output file path if successful, None otherwise.
    """
    # 1. Validate Input
    if file_path is None:
        if len(sys.argv) < 2:
            print("\n❌ Error: Please provide the JSON file path.")
            print("Usage: python recommendation_agent.py <path_to_lab_report.json>\n")
            return None
        file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found: {file_path}")
        return None

    # 2. Load Data
    print(f"\n📂 Loading report: {file_path}...")
    try:
        with open(file_path, 'r') as f:
            lab_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return None

    # 3. Run Analysis
    print("🧠 MedRecAgent is formulating the protocol... (This uses deep reasoning)")
    report = get_medical_recommendations(lab_data)
    
    if not report:
        print("❌ Failed to generate recommendations")
        return None

    # 4. Save & Print
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    input_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"PROTOCOL_{input_name}_{timestamp}.md"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("\n" + "="*60)
    print(report)
    print("="*60)
    print(f"\n✅ Medical Protocol saved to: {output_path}\n")
    
    return output_path

if __name__ == "__main__":
    main()