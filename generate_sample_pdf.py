import fitz  # PyMuPDF

def build_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size
    
    # Define a clean textbox rectangle
    rect = fitz.Rect(54, 54, 541, 788) # 0.75-inch margins (54 points)
    
    text = """FINTECH WEEKLY INTELLIGENCE - BI-MONTHLY UPDATE (MAY 2026)
Prepared by the Fintech Scout Research Group

This bi-monthly intelligence report highlights top early-stage and high-growth fintech companies showing massive commercial traction, strong organizational scaling, and impressive financial milestones.

---

1. PayNova (Payments & Checkout Solutions)
- Headquarters: Stockholm, Sweden
- Leadership: Carl Lindstrom (CEO & Founder), Freja Nilson (COO)
- Team Size: 42 employees
- Customer Traction: 920,000 active checkout users, expanding at an extraordinary 25% bimonthly growth rate.
- Financial Performance & Sales: Reported $14.5M in Annual Recurring Revenue (ARR), showing a 210% YoY increase in software sales.
- Funding: $8.5M Series A, backed by Creandum and EQT Ventures.
- Core Value: Providing dynamic, AI-driven embedded merchant checkout buttons that adapt dynamically to consumer purchase habits, reducing cart abandonment by 18%.

2. SaveSphere (WealthTech & Robo-Advisory)
- Headquarters: Singapore
- Leadership: Dev Patel (CEO & Co-founder), Samantha Koh (Chief Investment Officer)
- Team Size: 31 employees
- Customer Traction: 115,000 active retail investors, with total Assets Under Management (AUM) growing at 15% month-on-month.
- Financial Performance & Sales: Scaled sales and management fee revenue by 160% in the last 12 months, driven by their new smart-saving micro-pension product.
- Funding: $6.2M Seed stage round, backed by Vertex Ventures and Golden Gate Ventures.
- Core Value: Micro-fractional smart saving platform that rounds up daily card purchases into high-yielding automated ESG portfolios.

3. ShieldAudit (RegTech & AML Compliance)
- Headquarters: London, UK
- Leadership: Arthur Pendelton (CEO & Founder), Sarah Jenkins (CTO)
- Team Size: 28 employees
- Customer Traction: 45 institutional banking and enterprise clients, scaling up from 12 clients in the previous bimonthly period.
- Financial Performance & Sales: Subscription licensing sales grew by 130% YoY.
- Funding: $3.0M Seed funding, led by Balderton Capital.
- Core Value: Secure multi-party computation protocol to automate cross-border anti-money laundering (AML) compliance checks in real-time, reducing verification time from 48 hours to 3 seconds.
"""
    
    # Insert textbox with basic formatting
    page.insert_textbox(rect, text, fontsize=11, fontname="helv", align=0)
    
    output_filename = "sample_newsletter.pdf"
    doc.save(output_filename)
    doc.close()
    print(f"Successfully generated {output_filename} containing text-based fintech newsletter data.")

if __name__ == "__main__":
    build_pdf()
