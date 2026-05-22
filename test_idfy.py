import os
import research_agent
import db_manager
from dotenv import load_dotenv

load_dotenv()
db_manager.init_db()

print("Testing research_company with 'IDfy'...")
success, name = research_agent.research_company("IDfy")

if success:
    print(f"Success! Researched company and saved profile for: {name}")
    # Read the database
    all_comps = db_manager.get_all_companies()
    matching = [c for c in all_comps if c["name"].lower() == "idfy"]
    if matching:
        print(f"Database entry found: {matching[0]}")
    else:
        print("Not found in database!")
else:
    print(f"Failed! Output: {name}")
