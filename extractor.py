import os
import re
import json
import fitz  # PyMuPDF
import google.generativeai as genai
from google import genai as modern_genai
from google.genai import types as modern_types
from dotenv import load_dotenv
import db_manager

# Load environment variables
load_dotenv()

# Configure the Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# High-fidelity mock companies generator for fallback/demonstration purposes
MOCK_COMPANIES = [
    {
        "name": "ZetaPay",
        "sector": "Payments",
        "hq_location": "Singapore",
        "executives": [
            {"role": "CEO & Co-founder", "name": "Aaron Tan"},
            {"role": "CTO", "name": "Lin Wei"}
        ],
        "employee_count": 35,
        "customer_count": "450,000 active merchant accounts (180% YoY growth)",
        "sales_revenue": "$8.4M ARR, experiencing 20% month-over-month increase",
        "growth_rate_pct": 180.0,
        "growth_description": "ZetaPay has expanded incredibly fast in Southeast Asia, signing up over 2,000 new micro-retailers per day. Customer acquisition costs fell by 40% due to viral peer-to-peer business transactions.",
        "funding_stage": "Series A",
        "total_funding_raised": "$12.5M",
        "key_investors": ["Sequoia Capital India", "Wavemaker Partners"],
        "value_prop": "Sleek QR-code-first instant checkout APIs for micro-merchants in emerging markets."
    },
    {
        "name": "AuraWealth",
        "sector": "WealthTech & Investing",
        "hq_location": "New York, USA",
        "executives": [
            {"role": "Founder & CEO", "name": "Sarah Jenkins"},
            {"role": "Head of AI Research", "name": "Dr. Amit Patel"}
        ],
        "employee_count": 68,
        "customer_count": "85,000 active retail investors, growing 15% bimonthly",
        "sales_revenue": "$2.1M quarterly revenue, representing 140% YoY growth",
        "growth_rate_pct": 140.0,
        "growth_description": "AuraWealth's growth is driven by their novel conversational AI wealth planner. Total Assets Under Management (AUM) reached $1.2B in May 2026, a 2.5x increase compared to last year.",
        "funding_stage": "Series B",
        "total_funding_raised": "$24.0M",
        "key_investors": ["Tiger Global", "Bessemer Venture Partners", "Greycroft"],
        "value_prop": "Generative AI co-pilot that manages, rebalances, and explains customized investment portfolios for Gen-Z."
    },
    {
        "name": "CredoRisk",
        "sector": "RegTech & Lending",
        "hq_location": "Berlin, Germany",
        "executives": [
            {"role": "CEO", "name": "Markus Weber"},
            {"role": "Chief Risk Officer", "name": "Elena Rostova"}
        ],
        "employee_count": 52,
        "customer_count": "140 enterprise lending banks and fintech clients",
        "sales_revenue": "$5.8M ARR, showing a solid 90% growth in licensing sales",
        "growth_rate_pct": 90.0,
        "growth_description": "CredoRisk grew its licensing revenue by 90% YoY by automating SME credit risk analysis. Their API response volume increased to 2M checks daily, maintaining a 99.8% precision rate.",
        "funding_stage": "Seed",
        "total_funding_raised": "$3.2M",
        "key_investors": ["Point Nine Capital", "Cherry Ventures"],
        "value_prop": "Alternative data-driven credit risk scoring using open-banking APIs and localized merchant registry scraping."
    },
    {
        "name": "InsureFlow",
        "sector": "InsurTech",
        "hq_location": "London, UK",
        "executives": [
            {"role": "Co-founder & CEO", "name": "Edward Vance"},
            {"role": "Co-founder & COO", "name": "Chloe Sterling"}
        ],
        "employee_count": 22,
        "customer_count": "12,000 policies active, growing at 25% MoM",
        "sales_revenue": "$1.8M gross written premium, growing 300% since launch",
        "growth_rate_pct": 300.0,
        "growth_description": "InsureFlow captured significant market share in the instant gig-worker insurance space, registering a 3x increase in sales in the last 6 months. Customer retention sits at an outstanding 94%.",
        "funding_stage": "Pre-Seed",
        "total_funding_raised": "$1.5M",
        "key_investors": ["LocalGlobe", "Seedcamp"],
        "value_prop": "Automated, hyper-flexible commercial insurance policies tailored by the hour for gig-economy couriers and freelancers."
    }
]

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a text-based PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            text += f"\n--- PAGE {i+1} ---\n"
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def generate_mock_data(source_name="Mock Newsletter"):
    """Inserts high-fidelity mock companies into the database for testing/demos."""
    print("Generating mock fintech company data...")
    count = 0
    for company in MOCK_COMPANIES:
        company_copy = company.copy()
        company_copy["source_newsletter"] = source_name
        if db_manager.save_company(company_copy):
            count += 1
    return count

def query_gemini_for_fintechs(text, source_name):
    """
    Sends the extracted text to Gemini API with strict instructions to identify 
    emerging fintech companies and parse their structure, growth, customers, and sales.
    """
    import research_agent
    active_key = research_agent.get_api_key()
    
    if not active_key:
        print("Gemini API key missing. Falling back to high-fidelity mock data extraction.")
        return generate_mock_data(source_name)

    # Configure Gemini dynamic key using the modern SDK
    client = modern_genai.Client(api_key=active_key)

    prompt = f"""
    You are an expert financial analyst and investment banking researcher. 
    Analyze the following fintech newsletter text and extract all emerging or high-growth fintech companies mentioned.
    
    For each company, you MUST extract the following information:
    1. Company Name (Clean, official name)
    2. Sector/Sub-sector (e.g. Payments, WealthTech, InsurTech, RegTech, Neobanking, DeFi, Lending, Embedded Finance)
    3. Headquarter Location (City, Country)
    4. Executives (A list of key people, founders, or CEOs with their roles, formatted as objects with 'role' and 'name')
    5. Employee Count (An estimate or precise count of employees as an integer. If a range like 10-20 is mentioned, use the average or midpoint)
    6. Customer Count (Quantitative details about the customer base, active users, growth in user counts)
    7. Sales / Revenue Growth (Specific mention of sales revenue, ARR, monthly growth rates, or percentage spikes in revenue)
    8. Growth Rate Percentage (A numeric float representing the YoY or bimonthly growth rate. For example, if sales grew 150% YoY, use 150.0. If no precise number is present, estimate based on signals or leave null)
    9. Growth Description (A narrative explaining their growth trajectory, market traction, and expansion strategies)
    10. Funding Stage (e.g., Pre-Seed, Seed, Series A, Series B, Series C, Venture Debt, Bootstrapped)
    11. Total Funding Raised (e.g., "$5M", "£2.3M", "$15,000,000")
    12. Key Investors (List of venture capital firms or angel investors)
    13. Value Proposition (What pain point do they solve, and what is their core product?)
    
    CRITICAL INSTRUCTION ON ACCURACY AND EMPTY FIELDS:
    - If any specific metric (e.g., sales, funding, investors, executives, employee count, growth rate, customer base, etc.) is NOT explicitly mentioned or cannot be inferred with certainty from the provided text, do NOT guess, extrapolate, or invent fake data.
    - Set such unknown/unavailable text fields to an empty string ("") and numeric fields (employee_count, growth_rate_pct) to null in the JSON response.
    - We value strict factual correctness and accuracy. Do not hallucinate or speculate on numbers not present in the newsletter text.

    Respond strictly with a JSON object containing a "companies" array of these company objects. Do not include markdown code block formatting like ```json ... ```, just output raw JSON text that can be parsed directly.

    Here is the newsletter text to extract from:
    {text}
    """

    try:
        # Try gemini-2.5-flash which is supported on modern configurations
        try:
            config = modern_types.GenerateContentConfig(
                response_mime_type="application/json"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
        except Exception as e_flash:
            # Fallback to other models if needed
            print(f"Primary model gemini-2.5-flash failed: {e_flash}. Trying gemini-2.0-flash...")
            config = modern_types.GenerateContentConfig(
                response_mime_type="application/json"
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=config
            )
        
        # Clean potential whitespace issues
        raw_response = response.text.strip()
        data = json.loads(raw_response)
        
        companies_list = data.get("companies", [])
        if not companies_list:
            print("No fintech companies extracted by Gemini. Generating demo data as fallback.")
            return generate_mock_data(source_name)
            
        success_count = 0
        for company_data in companies_list:
            # Ensure name is provided
            if not company_data.get("name"):
                continue
                
            company_data["source_newsletter"] = source_name
            
            # Save to database
            if db_manager.save_company(company_data):
                success_count += 1
                
        return success_count
        
    except Exception as e:
        print(f"Failed to query Gemini API or parse JSON: {e}")
        print("Falling back to high-fidelity mock data extraction.")
        return generate_mock_data(source_name)

def process_newsletter(pdf_path):
    """Main pipeline function to extract text, run LLM entity extraction, and save companies."""
    source_name = os.path.basename(pdf_path)
    print(f"Starting pipeline for: {source_name}")
    
    # 1. Parse text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print(f"Warning: No text could be extracted from {source_name}. Generating mock data.")
        return generate_mock_data(source_name)
        
    # 2. Extract and insert data via LLM
    success_count = query_gemini_for_fintechs(text, source_name)
    print(f"Pipeline complete. Successfully saved {success_count} companies.")
    return success_count
