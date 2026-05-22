import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fintech_tracker.db")

def get_connection():
    """Returns a sqlite3 connection that resolves rows as dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the fintech_companies table with expanded fields for deep research
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fintech_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            sector TEXT,
            hq_location TEXT,
            founded_year TEXT,            -- Year the company was founded
            executives TEXT,             -- JSON string containing key executives details
            employee_count INTEGER,
            customer_count TEXT,          -- Details of customer metrics & growth
            sales_revenue TEXT,           -- Details of sales, ARR, or revenues
            growth_rate_pct REAL,         -- Numeric growth rate if available (e.g. 25.0 for 25% bimonthly)
            growth_description TEXT,      -- Detailed narrative about company's growth trajectory
            funding_stage TEXT,
            total_funding_raised TEXT,
            key_investors TEXT,
            value_prop TEXT,
            products TEXT,                -- Detailed description of core product lines
            transactions_ma TEXT,         -- Historic M&A deals, mergers, and funding details
            source_newsletter TEXT,       -- Name of source or "LLM Research Engine"
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_company(company_data):
    """
    Saves or updates a company in the database.
    Performs an upsert based on the unique company name.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert list/dict parameters to JSON string or plain text for SQLite storage
    executives = company_data.get("executives", "")
    if isinstance(executives, (list, dict)):
        executives = json.dumps(executives)
        
    key_investors = company_data.get("key_investors", "")
    if isinstance(key_investors, list):
        key_investors = ", ".join(key_investors)

    query = """
        INSERT INTO fintech_companies (
            name, sector, hq_location, founded_year, executives, employee_count, 
            customer_count, sales_revenue, growth_rate_pct, growth_description, 
            funding_stage, total_funding_raised, key_investors, value_prop, 
            products, transactions_ma, source_newsletter, extracted_at
        ) VALUES (
            :name, :sector, :hq_location, :founded_year, :executives, :employee_count, 
            :customer_count, :sales_revenue, :growth_rate_pct, :growth_description, 
            :funding_stage, :total_funding_raised, :key_investors, :value_prop, 
            :products, :transactions_ma, :source_newsletter, CURRENT_TIMESTAMP
        )
        ON CONFLICT(name) DO UPDATE SET
            sector = COALESCE(EXCLUDED.sector, sector),
            hq_location = COALESCE(EXCLUDED.hq_location, hq_location),
            founded_year = COALESCE(EXCLUDED.founded_year, founded_year),
            executives = COALESCE(EXCLUDED.executives, executives),
            employee_count = COALESCE(EXCLUDED.employee_count, employee_count),
            customer_count = COALESCE(EXCLUDED.customer_count, customer_count),
            sales_revenue = COALESCE(EXCLUDED.sales_revenue, sales_revenue),
            growth_rate_pct = COALESCE(EXCLUDED.growth_rate_pct, growth_rate_pct),
            growth_description = COALESCE(EXCLUDED.growth_description, growth_description),
            funding_stage = COALESCE(EXCLUDED.funding_stage, funding_stage),
            total_funding_raised = COALESCE(EXCLUDED.total_funding_raised, total_funding_raised),
            key_investors = COALESCE(EXCLUDED.key_investors, key_investors),
            value_prop = COALESCE(EXCLUDED.value_prop, value_prop),
            products = COALESCE(EXCLUDED.products, products),
            transactions_ma = COALESCE(EXCLUDED.transactions_ma, transactions_ma),
            source_newsletter = COALESCE(EXCLUDED.source_newsletter, source_newsletter),
            extracted_at = CURRENT_TIMESTAMP
    """
    
    try:
        cursor.execute(query, {
            "name": company_data.get("name"),
            "sector": company_data.get("sector"),
            "hq_location": company_data.get("hq_location"),
            "founded_year": company_data.get("founded_year"),
            "executives": executives,
            "employee_count": company_data.get("employee_count"),
            "customer_count": company_data.get("customer_count"),
            "sales_revenue": company_data.get("sales_revenue"),
            "growth_rate_pct": company_data.get("growth_rate_pct"),
            "growth_description": company_data.get("growth_description"),
            "funding_stage": company_data.get("funding_stage"),
            "total_funding_raised": company_data.get("total_funding_raised"),
            "key_investors": key_investors,
            "value_prop": company_data.get("value_prop"),
            "products": company_data.get("products"),
            "transactions_ma": company_data.get("transactions_ma"),
            "source_newsletter": company_data.get("source_newsletter", "LLM Research Engine")
        })
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error saving company {company_data.get('name')}: {e}")
        conn.rollback()
        success = False
    finally:
        conn.close()
    
    return success

def get_all_companies():
    """Returns all companies in the database as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fintech_companies ORDER BY name ASC")
    rows = cursor.fetchall()
    
    companies = []
    for row in rows:
        company = dict(row)
        # Parse executives back from JSON if it looks like JSON
        if company["executives"]:
            try:
                company["executives_parsed"] = json.loads(company["executives"])
            except Exception:
                company["executives_parsed"] = company["executives"]
        else:
            company["executives_parsed"] = []
            
        companies.append(company)
        
    conn.close()
    return companies

def clear_database():
    """Clears all records from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fintech_companies")
    conn.commit()
    conn.close()

# Initialize DB on first import
init_db()
