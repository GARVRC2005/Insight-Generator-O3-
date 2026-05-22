import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    api_key = api_key.strip().strip("'\"")

client = genai.Client(api_key=api_key)

company_name = "IDfy"

prompt = f"""
    You are an expert Investment Banking Research Analyst. Research the fintech company called '{company_name}'.
    Compile its key business metrics, product offerings, growth milestones, active users, revenues, past M&A (Mergers & Acquisitions) deals, funding transactions, founding details, headquarters, and key executives.
    Note: If the company is from India, please emphasize its integration with UPI, its status in the Indian fintech market, and domestic regulators (RBI).

    For the company, you MUST compile the following information. Be as realistic, accurate, and detailed as possible:
    1. name: Clean, official name
    2. sector: Sub-sector (e.g. Payments, WealthTech, InsurTech, RegTech, Neobanking, DeFi, Lending, Embedded Finance)
    3. hq_location: Headquarters City, Country (e.g., "Bengaluru, India" if applicable)
    4. founded_year: Year founded (e.g. "2015")
    5. executives: List of key people, founders, or CEOs with their roles, formatted as objects with 'role' and 'name'
    6. employee_count: Integer estimate of current employee headcount. If a range is mentioned, use the midpoint.
    7. customer_count: Description of the customer base, active users, or account growth metrics.
    8. sales_revenue: Quantitative description of revenue, ARR, gross margins, or recent financial reports.
    9. growth_rate_pct: A float representing the YoY or bimonthly growth rate of customers or sales (e.g. 35.0 for 35% growth).
    10. growth_description: Narrative detailing their growth trajectory, geographic expansion, and key scaling drivers.
    11. funding_stage: Current stage (e.g., Seed, Series A, Series B, Series C, Series D, Public, Private)
    12. total_funding_raised: Total raised (e.g. "$734M", "$1.2B")
    13. key_investors: List or description of venture capital backers and angels
    14. value_prop: One or two sentence core value proposition.
    15. products: Detailed description of their core product lines and software products.
    16. transactions_ma: Detailed narrative of past transaction deals, acquisitions made, mergers, IPO milestones, or massive strategic fundraises.

    CRITICAL INSTRUCTION ON ACCURACY AND EMPTY FIELDS:
    - Many fintech companies are early-stage or private and do not have publicly available financial or customer data. 
    - If any specific metric (e.g., sales_revenue, total_funding_raised, key_investors, executives, employee_count, growth_rate_pct, customer_count, etc.) is NOT publicly known, do NOT guess, extrapolate, or invent fake data.
    - Set such unknown/unavailable text fields to an empty string ("") and numeric fields (employee_count, growth_rate_pct) to null in the JSON response.
    - We value strict factual correctness and accuracy over completeness. Hallucinations or made-up statistics are strictly forbidden.

    Respond with a valid JSON block containing these keys. Wrap the JSON block in a markdown code block starting with ```json and ending with ```.

    Company Name to Scour: {company_name}
    """

print("Calling gemini-2.5-flash-lite WITHOUT search grounding...")
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=prompt
)

print(f"Response: {response}")
print(f"Response.text: {response.text}")
if response.candidates:
    print(f"Candidates: {response.candidates}")
    for idx, c in enumerate(response.candidates):
        print(f"Candidate {idx} finish_reason: {c.finish_reason}")
        print(f"Candidate {idx} content: {c.content}")


