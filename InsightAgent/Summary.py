import sys
import json
import os
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
# Get API Key from environment variable (passed from Node.js or set in .env)
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GOOGLE_GEMINI_API_KEY environment variable not set")
    sys.exit(1)

OUTPUT_FOLDER = "summary_output"

# List of models to try in order (fallback system)
MODELS_TO_TRY = [
    'gemini-2.5-flash',           # Latest, most capable
    'gemini-flash-latest',        # Alias to latest stable
    'gemini-2.0-flash-lite',      # Lighter weight, better quota
    'gemini-2.5-flash-lite',      # Alternative lite version
]

def get_clinical_insight(json_data):
    """
    Sends the raw JSON data to Gemini with the ClinicalInsightAgent persona.
    Tries multiple models if quota is exceeded.
    """
    genai.configure(api_key=API_KEY)
    
    # Try each model in sequence
    for model_name in MODELS_TO_TRY:
        try:
            print(f"🔄 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)

            # The System Prompt: Defines the AI's persona and logic
            # REFINED FOR SIMPLICITY AND HUMAN-FRIENDLINESS
            prompt = f"""
        You are 'ClinicalInsightAgent', a warm, friendly, and clear AI health assistant. 
        Think of yourself as a kind doctor explaining results to a patient who has ZERO medical background.

        GOAL:
        Translate the provided Medical Lab Report (JSON) into a simple story about the patient's health.
        **AVOID COMPLEX JARGON.** If you must use a medical term, explain it immediately with a simple real-world analogy.

        INPUT DATA:
        {json.dumps(json_data, indent=2)}

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

            response = model.generate_content(prompt)
            print(f"✅ Successfully used model: {model_name}")
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            # Check if it's a quota error
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️  Quota exceeded for {model_name}, trying next model...")
                continue  # Try next model
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"⚠️  Model {model_name} not available, trying next...")
                continue  # Try next model
            else:
                # Other error, return it
                return f"Error communicating with AI ({model_name}): {str(e)}"
    
    # If all models failed
    return "❌ All Gemini models exceeded quota or unavailable. Please try again later or wait for quota reset."

def main(file_path=None):
    """
    Main function to run the Clinical Insight Agent.
    Returns the output file path if successful, None otherwise.
    """
    # 1. Check if the user provided a file path
    if file_path is None:
        if len(sys.argv) < 2:
            print("\n❌ Error: No file path provided.")
            print("Usage: python clinical_agent.py <path_to_json_file>")
            print("Example: python clinical_agent.py report.json\n")
            return None
        file_path = sys.argv[1]

    # 2. Check if file exists
    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found at '{file_path}'")
        return None

    # 3. Read and Parse JSON
    print(f"\n📂 Reading file: {file_path}...")
    try:
        with open(file_path, 'r') as f:
            lab_data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Error: The file is not valid JSON.")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

    # 4. Generate Analysis
    print("🧠 ClinicalInsightAgent is analyzing the data... (Please wait)")
    analysis = get_clinical_insight(lab_data)
    
    if not analysis:
        print("❌ Failed to generate clinical analysis")
        return None

    # 5. Save to file
    # Create output folder if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{input_filename}_summary_{timestamp}.txt"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Write analysis to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("CLINICAL INSIGHT AGENT - LAB REPORT ANALYSIS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source File: {file_path}\n")
        f.write("="*70 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "="*70 + "\n")

    # 6. Output Result
    print("\n" + "="*50)
    print("REPORT ANALYSIS")
    print("="*50 + "\n")
    print(analysis)
    print("\n" + "="*50)
    print(f"\n✅ Summary saved to: {output_path}")
    print(f"📁 Output folder: {os.path.abspath(OUTPUT_FOLDER)}\n")
    
    return output_path

if __name__ == "__main__":
    main()