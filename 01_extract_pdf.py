import pypdf
import os
import csv

# --- CONFIGURATION ---
PDF_NAME = "data/raw/gao_report.pdf" 
OUTPUT_CSV = "data/processed/navair_matches.csv"

# Auto-create the processed folder if it doesn't exist
os.makedirs("data/processed", exist_ok=True)

# --- THE MASTER NAVAIR COST ONTOLOGY (Dictionary format for Auto-Tagging) ---
ONTOLOGY = {
    "FUNDING": [
        "rdt&e", "apn", "wpn", "o&m", "milcon", "opn", "scn", "panmc", 
        "base year", "then year", "constant year", "by$", "ty$", "cy$",
        "total obligation authority", "toa", "budget authority", "appropriation",
        "p-1", "r-1", "presidents budget", "pb24", "pb25", "pb26", "unfunded requirement"
    ],
    "WBS": [
        "flyaway cost", "weapon system cost", "procurement cost", "pauc", "apuc",
        "se/pm", "st&e", "software", "non-recurring", "recurring", "engineering change",
        "airframe", "propulsion", "avionics", "payload", "integration", "training",
        "support equipment", "initial spares", "peculiar support", "facilities"
    ],
    "CONTRACT": [
        "firm fixed price", "ffp", "cost plus", "cpff", "cpif", "fpif", "cpaf",
        "incentive fee", "award fee", "undefinitized", "uca", "idiq", "ota", 
        "other transaction authority", "sole source", "period of performance", "pop",
        "prime contractor", "subcontractor", "vendor"
    ],
    "SCHEDULE": [
        "milestone a", "milestone b", "milestone c", "ioc", "foc", "lrip", "frp",
        "preliminary design review", "pdr", "critical design review", "cdr", 
        "system requirements review", "srr", "first flight", "delivery", "concurrency"
    ],
    "RISK": [
        "cost variance", "schedule variance", "cv", "sv", "nunn-mccurdy", "breach", 
        "eac", "estimate at completion", "bac", "budget at completion", "etc",
        "management reserve", "contingency", "schedule margin", "technical risk",
        "independent cost estimate", "ice", "program office estimate", "poe",
        "dcaa", "dcma", "cape", "caig"
    ],
    "METHODS": [
        "parametric", "analogous", "bottom-up", "learning curve", "step-down",
        "rate curve", "inflation", "escalation", "monte carlo", "s-curve",
        "confidence level", "employment cost index", "eci"
    ]
}

def run_extraction():
    # Pre-flight check
    if not os.path.exists(PDF_NAME):
        print(f"ERROR: '{PDF_NAME}' not found.")
        print("Please make sure your PDF is in the 'data/raw' folder!")
        return

    try:
        reader = pypdf.PdfReader(PDF_NAME)
        total_pages = len(reader.pages)
        print(f"--- Scouting {total_pages} pages with Pro NAVAIR Ontology ---")
        
        all_matches = []

        for i in range(total_pages):
            page_text = reader.pages[i].extract_text()
            if not page_text:
                continue
                
            lines = page_text.split('\n')
            
            for index, line in enumerate(lines):
                line_lower = line.lower()
                found_match = False
                
                # Check the line against our categorized dictionary
                for category, terms in ONTOLOGY.items():
                    for term in terms:
                        if term in line_lower:
                            # Grab the context (1 line before, current line, 1 line after)
                            start = max(0, index - 1)
                            end = min(len(lines), index + 2)
                            context = " | ".join([l.strip() for l in lines[start:end]])
                            
                            all_matches.append({
                                "Page": i + 1,        # Added +1 so page numbers match the PDF reader exactly
                                "Category": category, # This is the new Auto-Tag feature!
                                "Term": term.upper(),
                                "Context": context
                            })
                            found_match = True
                            break # Break the term loop to avoid double-counting the same line
                            
                    if found_match:
                        break # Break the category loop, move to the next line in the document

        # --- WRITE DIRECTLY TO CSV ---
        keys = ["Page", "Category", "Term", "Context"]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_matches)
            
        print(f"\n✅ SUCCESS! Extracted {len(all_matches)} targeted matches.")
        print(f"Saved to: {OUTPUT_CSV}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_extraction()