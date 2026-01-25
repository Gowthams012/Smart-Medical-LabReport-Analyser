"""
Root Pipeline for Clinical Insight Agent
Generates both Summary and Medical Recommendations from Lab Reports
"""

import sys
import json
import os
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
API_KEY = "AIzaSyDglDom7L5g14WGjcxuVKZLv--jJggOolE"

SUMMARY_OUTPUT_FOLDER = "summary_output"
RECOMMENDATION_OUTPUT_FOLDER = "medical_recommendations"

# List of models to try in order (fallback system)
MODELS_TO_TRY = [
    'gemini-2.5-flash',           # Latest, most capable
    'gemini-flash-latest',        # Alias to latest stable
    'gemini-2.0-flash-lite',      # Lighter weight, better quota
    'gemini-2.5-flash-lite',      # Alternative lite version
]

def generate_ai_response(json_data, prompt_template, agent_name):
    """
    Generic AI response generator with fallback system
    """
    genai.configure(api_key=API_KEY)
    
    # Try each model in sequence
    for model_name in MODELS_TO_TRY:
        try:
            print(f"🔄 Trying model: {model_name} for {agent_name}")
            model = genai.GenerativeModel(model_name)
            
            prompt = prompt_template.format(data=json.dumps(json_data, indent=2))
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
                return f"Error with AI ({model_name}): {str(e)}"
    
    return f"❌ All Gemini models exceeded quota or unavailable for {agent_name}."

def get_clinical_summary(json_data):
    """Generate human-friendly clinical summary"""
    prompt_template = """
You are 'ClinicalInsightAgent', a warm, friendly, and clear AI health assistant. 
Think of yourself as a kind doctor explaining results to a patient who has ZERO medical background.

GOAL:
Translate the provided Medical Lab Report (JSON) into a simple story about the patient's health.
**AVOID COMPLEX JARGON.** If you must use a medical term, explain it immediately with a simple real-world analogy.

INPUT DATA:
{data}

OUTPUT GUIDELINES (Use Basic English):

1.  **The "Big Picture" (Executive Summary)**:
    -   Start with a friendly greeting.
    -   Give a 3-sentence summary. Is the engine running smoothly? Or does it need a tune-up?
    -   Use clear phrases like "Overall, you are in great shape!" or "There are a few things we need to watch."

2.  **What the Results Mean (Detailed Analysis)**:
    -   Don't just list numbers. Group them logically (e.g., "Blood Health," "Liver Health," "Energy Levels").
    -   For each key result:
        -   **What is it?** Use an analogy! (e.g., "Hemoglobin is like a delivery truck for oxygen.")
        -   **Your Status:** Use simple terms: "Normal," "A bit low," "A bit high."
        -   **Why it matters:** Explain the feeling or risk (e.g., "Low levels might make you feel tired.").
    -   Use Emojis visually: ✅ (Good), ⚠️ (Caution), 🚨 (Needs Attention).

3.  **Connecting the Dots (Correlations)**:
    -   Explain if one result is affecting another.
    -   Example: "Since your hydration is low, that might be why your concentration levels are off."

4.  **Simple Next Steps (Actionable Recommendations)**:
    -   Give 3 very specific, easy things to do *tomorrow*.
    -   Bad: "Improve diet."
    -   Good: "Try adding a handful of spinach to your lunch" or "Drink one extra glass of water before breakfast."

5.  **Important Note (Disclaimer)**:
    -   Remind them gently that you are an AI helper, not a replacement for their real doctor.

FORMAT:
-   Use short paragraphs.
-   Use bullet points.
-   Keep the tone conversational and encouraging.
"""
    return generate_ai_response(json_data, prompt_template, "Summary Agent")

def get_medical_recommendations(json_data):
    """Generate medical recommendations and action protocol"""
    prompt_template = """
You are 'MedRecAgent', a highly advanced Clinical Decision Support System.

YOUR GOAL: 
Analyze the patient's lab report and generate a **strict, safety-focused Action Protocol**.

CRITICAL INSTRUCTION: 
You must be highly specific. Do not just say "eat healthy." 
You must recommend specific foods that chemically interact with the patient's specific abnormal markers.

INPUT LAB DATA:
{data}

--- OUTPUT STRUCTURE (Use Markdown) ---

## 🏥 Clinical Status Snapshot
(1 bullet point summarizing the primary concern. e.g., "Patient indicates pre-diabetic markers with elevated liver enzymes.")

## 📋 The Protocol: Immediate Actions
*Analyze the specific abnormal values and provide targeted advice.*

### ✅ WHAT TO DO (Protective Actions)
*List 3-4 specific, science-backed interventions.*
* **Dietary:** (e.g., "Since Iron is low, introduce heme-iron sources like lean red meat or non-heme sources like lentils with Vitamin C.")
* **Lifestyle:** (e.g., "Implement 'Zone 2' cardio training to assist with lipid oxidation.")
* **Supplementation (General):** (e.g., "Consider discussing Vitamin D3 + K2 with your doctor due to low levels.")

### ⛔ WHAT TO AVOID (Contraindications)
*This is CRITICAL. Tell them what behaviors/foods will spike their bad numbers.*
* **Dietary Hazards:** (e.g., "Strictly limit fructose and alcohol as your Uric Acid is elevated; these will trigger gout.")
* **Lifestyle Risks:** (e.g., "Avoid high-intensity lifting until blood pressure stabilizes.")

## 🔬 Deep Medical Intelligence (Correlations)
*Explain ONE hidden connection in their data.*
(e.g., "Your High TSH combined with High Cholesterol is a classic pattern. Treating the Thyroid often lowers the Cholesterol automatically.")

## 🩺 Next Clinical Steps
* "Re-test [Test Name] in [Number] weeks."
* "Schedule appointment with [Specialist Type] (e.g., Endocrinologist)."

---
**DISCLAIMER:** *I am an AI Recommendation Agent, not a doctor. This report is for educational purposes and should be reviewed by a certified medical professional before starting any new treatment.*
"""
    return generate_ai_response(json_data, prompt_template, "Recommendation Agent")

def save_output(content, folder, filename_prefix, source_file):
    """Save output to file with timestamp"""
    os.makedirs(folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_filename = os.path.splitext(os.path.basename(source_file))[0]
    output_filename = f"{input_filename}_{filename_prefix}_{timestamp}.txt"
    output_path = os.path.join(folder, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"CLINICAL INSIGHT AGENT - {filename_prefix.upper()}\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source File: {source_file}\n")
        f.write("="*70 + "\n\n")
        f.write(content)
        f.write("\n\n" + "="*70 + "\n")
    
    return output_path

def main():
    print("\n" + "="*70)
    print("🏥 CLINICAL INSIGHT AGENT - ROOT PIPELINE")
    print("="*70 + "\n")
    
    # 1. Validate Input
    if len(sys.argv) < 2:
        print("❌ Error: No file path provided.")
        print("\nUsage: python root.py <path_to_json_file>")
        print("Example: python root.py report.json\n")
        sys.exit(1)

    file_path = sys.argv[1]

    # 2. Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at '{file_path}'\n")
        sys.exit(1)

    # 3. Read and Parse JSON
    print(f"📂 Reading lab report: {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lab_data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Error: The file is not valid JSON.\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}\n")
        sys.exit(1)

    print("✅ Lab report loaded successfully!\n")

    # 4. Generate Summary
    print("="*70)
    print("📝 STEP 1: Generating Clinical Summary...")
    print("="*70)
    summary = get_clinical_summary(lab_data)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    print(summary)
    
    summary_path = save_output(summary, SUMMARY_OUTPUT_FOLDER, "summary", file_path)
    print(f"\n✅ Summary saved to: {summary_path}")

    # 5. Generate Recommendations
    print("\n" + "="*70)
    print("💊 STEP 2: Generating Medical Recommendations...")
    print("="*70)
    recommendations = get_medical_recommendations(lab_data)
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70 + "\n")
    print(recommendations)
    
    recommendations_path = save_output(recommendations, RECOMMENDATION_OUTPUT_FOLDER, "recommendations", file_path)
    print(f"\n✅ Recommendations saved to: {recommendations_path}")

    # 6. Summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📁 Outputs:")
    print(f"   Summary: {os.path.abspath(summary_path)}")
    print(f"   Recommendations: {os.path.abspath(recommendations_path)}")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
