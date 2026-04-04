import pandas as pd
import os
import re

# --- CONFIGURATION ---
INPUT_FILE = "data/processed/navair_matches.csv"
OUTPUT_FILE = "data/processed/navair_matches_CLEANED.csv"

def run_cleaning():
    # Pre-flight check
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' not found. Run your Scout script first!")
        return

    try:
        print("--- Loading Raw Scout Data ---")
        df = pd.read_csv(INPUT_FILE)
        original_count = len(df)
        print(f"Original rows: {original_count}")

        # --- THE WASHING MACHINE (Pro Level) ---
        
        # A. Drop exact duplicates (Sometimes the scout catches the same sentence twice)
        df = df.drop_duplicates(subset=['Context'])
        
        # B. Filter out "Junk" rows (Contexts that are too short to be useful)
        df = df[df['Context'].str.len() > 40]

        # C. Filter out Table of Contents "Dot Leaders" (e.g., "Cost Variance.......... Page 42")
        df = df[~df['Context'].str.contains(r'\.{5,}', regex=True, na=False)]
        
        # D. Deep Text Formatting (The Scrub)
        # 1. Remove the " | " pipe dividers we added in the scout
        df['Context'] = df['Context'].str.replace(' | ', ' ', regex=False)
        # 2. Strip out all weird PDF line breaks
        df['Context'] = df['Context'].str.replace('\r\n', ' ', regex=False)
        df['Context'] = df['Context'].str.replace('\n', ' ', regex=False)
        # 3. Collapse multiple spaces into a single space using Regex
        df['Context'] = df['Context'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip())
        
        # E. Remove GAO Boilerplate headers/footers
        # This catches things like "Page 42 GAO-24-106048 Weapon Systems Assessment"
        df['Context'] = df['Context'].apply(lambda x: re.sub(r'Page \d+ GAO-\d+-\d+.*?Assessment', '', str(x)))

        # --- THE ARCHITECT (Sorting) ---
        # Look at this new sort! Category -> Term -> Page
        df = df.sort_values(by=['Category', 'Term', 'Page'])

        # --- SAVE & EXPORT ---
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        
        final_count = len(df)
        print("\n--- Cleaning Complete ---")
        print(f"Removed {original_count - final_count} useless or duplicate rows.")
        print(f"✅ Clean, categorized data saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error during cleaning: {e}")

if __name__ == "__main__":
    run_cleaning()