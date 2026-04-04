import os
import pandas as pd
from google import genai
from dotenv import load_dotenv

# 1. UNLOCK THE VAULT
load_dotenv()
MY_API_KEY = os.getenv("GEMINI_API_KEY")

# --- CONFIGURATION ---
INPUT_CSV = "data/processed/navair_matches_CLEANED.csv"
OUTPUT_REPORT = "outputs/ai_analysis_report.txt"

os.makedirs("outputs", exist_ok=True)

def run_ai_analysis():
    # 2. LOAD YOUR CLEAN DATA
    if not os.path.exists(INPUT_CSV):
        print(f"Error: '{INPUT_CSV}' not found! Run '02_cleaner.py' first.")
        return
    
    print("--- Loading Cleaned CSV Data ---")
    df = pd.read_csv(INPUT_CSV)

    # 3. FILTER FOR HIGH-VALUE RISK DATA
    # The 3.1 Pro model is smart enough to handle 50 rows of data at once.
    risk_terms = ['COST VARIANCE', 'NUNN-MCCURDY', 'BREACH', 'EAC', 'LEARNING CURVE']
    analysis_data = df[df['Term'].isin(risk_terms)].head(50)

    if len(analysis_data) == 0:
        print("No extreme risk terms found. Analyzing general matches...")
        analysis_data = df.head(50)

    # 4. BUILD THE CONTEXT BLOCK
    data_string = ""
    for _, row in analysis_data.iterrows():
        data_string += f"[PAGE {row['Page']}] (Category: {row['Term']}): {row['Context']}\n\n"

    # 5. THE NAVAIR PROMPT (The "SME" Persona)
    prompt = f"""
    SYSTEM INSTRUCTIONS:
    You are a Senior NAVAIR Acquisition Expert and Lead Cost Estimator. 
    Analyze the following fragments from the Weapon Systems Annual Assessment.
    
    GOAL:
    1. Identify the Top 3 systemic financial risks across the programs mentioned.
    2. Extract and quantify cost growth in dollar amounts or percentages.
    3. Look for "hidden" risks where schedule slips are likely to drive future cost growth.
    4. Provide an executive BLUF for a Flag Officer (Admiral level).

    DATA:
    {data_string}
    """

    # 6. CALL THE AI
    print("--- Requesting Strategic Analysis from Gemini---")
    print("--- (Note: This is a high-reasoning model and may take a moment to 'think') ---")
    
    try:
        client = genai.Client(api_key=MY_API_KEY)
        
        # Using the absolute smartest model from your list
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        
        print("\n" + "="*60)
        print("NAVAIR STRATEGIC COST ANALYSIS (3.1 PRO)")
        print("="*60)
        print(response.text)
        print("="*60)
        
        # Save the report
        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\nStrategic report saved to: {OUTPUT_REPORT}")
            
    except Exception as e:
        if "429" in str(e):
            print("\nError: Rate Limit Reached. Pro models have stricter limits (usually 2 per minute).")
            print("Wait 60 seconds and try again.")
        else:
            print(f"AI Call failed: {e}")

if __name__ == "__main__":
    run_ai_analysis()