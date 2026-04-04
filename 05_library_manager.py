import sqlite3
import pandas as pd
import os

# --- CONFIG ---
DB_NAME = "navair_knowledge_base.db"
CLEAN_CSV = "data/processed/navair_matches_CLEANED.csv"

def setup_database():
    """Create the 'Memory Bank' structure (Now with Category & Year)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # We added 'report_year' and 'category' to the blueprint
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_doc TEXT,
            report_year INTEGER,
            category TEXT,
            term TEXT,
            page_num INTEGER,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database blueprint '{DB_NAME}' is ready.")

def ingest_findings(program_name, report_year):
    """Move data from CSV into the Database safely"""
    if not os.path.exists(CLEAN_CSV):
        print("❌ Error: No cleaned CSV found to ingest.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # SAFETY CHECK: If we already ingested this exact report, delete the old rows first
    # This prevents doubling your data if you run the script twice!
    cursor.execute("DELETE FROM cost_findings WHERE source_doc = ? AND report_year = ?", (program_name, report_year))
    conn.commit()

    # Load the new data
    df = pd.read_csv(CLEAN_CSV)
    
    # Add our "Timeline" and "Source" tags
    df['source_doc'] = program_name
    df['report_year'] = report_year
    
    # Map the CSV columns to match our Database columns exactly
    df = df.rename(columns={
        'Page': 'page_num', 
        'Category': 'category', 
        'Term': 'term', 
        'Context': 'context'
    })
    
    # Deposit the data into the vault
    df.to_sql('cost_findings', conn, if_exists='append', index=False)
    conn.close()
    print(f"✅ Ingested {len(df)} categorized findings for {program_name} ({report_year}).")

def search_library(keyword):
    """Find specific intelligence and see its history"""
    conn = sqlite3.connect(DB_NAME)
    
    # Now we pull the year and category too!
    query = f"""
        SELECT report_year, source_doc, category, page_num, context 
        FROM cost_findings 
        WHERE context LIKE '%{keyword}%' OR term LIKE '%{keyword}%'
        ORDER BY report_year DESC
    """
    results = pd.read_sql(query, conn)
    conn.close()
    
    print(f"\n--- Intelligence Report for: '{keyword.upper()}' ---")
    if results.empty:
        print("No matches found in your knowledge bank.")
    else:
        for i, row in results.iterrows():
            print(f"[{row['report_year']} | {row['source_doc']} | {row['category']} - Pg {row['page_num']}]:")
            print(f"   {row['context'][:150]}...\n")
    
    return results

if __name__ == "__main__":
    setup_database()
    
    # Now when you ingest, you pass the program name AND the year of the report
    ingest_findings("Sentinel LGM-35A", 2024)
    
    # Let's test the search engine to see how it looks
    search_library("breach")