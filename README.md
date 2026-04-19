<img width="2111" height="833" alt="3ad56385-567f-4743-8c9f-023937b83fc1" src="https://github.com/user-attachments/assets/1f9c39ee-752c-4a0b-9b3c-6835d19457fb" />
Automated AI Cost Extraction Pipeline
Executive Summary
I developed this system to handle the tedious task of digging through complex, unstructured PDF documents to find specific cost data. Instead of wasting hours on manual data entry, this pipeline uses Python and Google's Gemini AI to automatically find, clean, and store financial information. It captures both text and visual data (like tables and charts), analyzes the context, and saves the final results into a structured database. This project effectively turns a manual bottleneck into an automated, scalable workflow.

The Technical Workflow
The system is broken down into a five-step modular pipeline to ensure data accuracy and efficiency:

Extracting Text (01_extract_pdf.py): This is the ingestor that reads raw PDF files and converts them into text that the computer can process.

Data Cleaning (02_cleaner.py): Raw PDF text is usually messy. This script scrubs the data, removes formatting errors, and prepares the text for the AI.

AI Analysis (03_ai_analyst.py): This is the brain of the operation. It feeds the cleaned data to the Gemini API to identify and extract specific cost metrics.

Visual Extraction (04_visual_extractor.py): Since important data is often buried in charts or graphs, this script uses vision-based analysis to interpret images within the documents.

Database Management (05_library_manager.py): The final step takes all the findings and logs them into a local SQLite database while also generating a CSV report for easy viewing.

Setup and Installation
Clone the project:
Download the repository to your local machine.

Install the environment:
I used a requirements file to keep the project lightweight. You can install all necessary libraries with:
pip install -r requirements.txt

Configure your API key:
You will need a Gemini API key to run the analyst scripts. Create a file named .env in the root folder and add your key:
GEMINI_API_KEY=your_actual_key_here

Security and Project Hygiene
I built this repository with security in mind. I implemented a strict .gitignore file to ensure that sensitive files like API keys, large virtual environments, and local data exports are never uploaded to the public history. This keeps the repository clean, professional, and secure for deployment.
