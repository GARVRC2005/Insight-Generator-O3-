import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import db_manager
import research_agent
import json
import os
import re

# Page configurations for a wide, beautiful desktop dashboard
st.set_page_config(
    page_title="Indian & Global Fintech Scout - Investment Banking Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Mode, Sleek HSL Accents, Glassmorphism, and Jakarta Sans)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Font override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main App Background Override */
    .stApp {
        background-color: #0c0e12;
        color: #c5c6c7;
    }
    
    /* Premium Title Container */
    .header-box {
        padding: 2.5rem;
        background: linear-gradient(135deg, #161b22 0%, #0c0e12 100%);
        border-radius: 20px;
        border: 1px solid rgba(102, 252, 241, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .header-box::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #66fcf1 0%, #45f3ff 50%, #00ff88 100%);
    }
    
    .header-badge {
        display: inline-block;
        background: rgba(102, 252, 241, 0.1);
        color: #66fcf1;
        border: 1px solid rgba(102, 252, 241, 0.3);
        border-radius: 30px;
        padding: 0.3rem 1rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1rem;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    .header-title {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.06rem;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    }
    
    .header-desc {
        font-size: 1.05rem;
        color: #8b949e;
        margin-top: 0.8rem;
        max-width: 900px;
        line-height: 1.5;
    }
    
    /* Glassmorphic Cards */
    .metric-card {
        background: rgba(22, 27, 34, 0.75);
        border: 1px solid rgba(102, 252, 241, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: left;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(102, 252, 241, 0.4);
        box-shadow: 0 8px 30px rgba(102, 252, 241, 0.12);
    }
    
    .metric-num {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03rem;
    }
    
    .metric-name {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08rem;
        color: #66fcf1;
        margin-bottom: 0.4rem;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #8b949e;
        margin-top: 0.3rem;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
    }
    
    /* Section dividers */
    .section-title {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        border-bottom: 2px solid rgba(102, 252, 241, 0.15);
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1.2rem;
    }
    
    /* Key Details Box */
    .profile-details-box {
        background: rgba(22, 27, 34, 0.45);
        border: 1px solid rgba(197, 198, 199, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        min-height: 380px;
        height: 100%;
        box-sizing: border-box;
    }
    
    .stat-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        color: #66fcf1;
    }
    
    .stat-value {
        font-size: 1rem;
        color: #ffffff;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    /* Interactive Forecaster Block */
    .forecaster-panel {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.8) 0%, rgba(13, 15, 20, 0.9) 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize SQLite database
db_manager.init_db()

# Pre-populate empty database with initial high-fidelity Indian companies
companies_in_db = db_manager.get_all_companies()
if not companies_in_db:
    # Pre-populate with flagship Indian fintech giants: Razorpay, Zerodha, and Paytm
    db_manager.save_company(research_agent.MOCK_DATABASE["razorpay"])
    db_manager.save_company(research_agent.MOCK_DATABASE["zerodha"])
    db_manager.save_company(research_agent.MOCK_DATABASE["paytm"])
    db_manager.save_company(research_agent.MOCK_DATABASE["phonepe"])
    db_manager.save_company(research_agent.MOCK_DATABASE["cred"])
    
    # Refresh companies list
    companies_in_db = db_manager.get_all_companies()

# --- SIDEBAR: Scour and Search Controls ---
with st.sidebar:
    st.markdown("<h3 style='color: #66fcf1; margin-top:0;'>🔍 Indian Fintech Engine</h3>", unsafe_allow_html=True)
    st.write("Input the name of any global or Indian fintech company. The LLM scours the internet to generate a comprehensive analytical profile, saving the data dynamically into SQLite.")
    
    research_input = st.text_input("Enter Fintech Name", placeholder="e.g. Razorpay, Paytm, CRED, PhonePe")
    
    if st.button("🚀 Scour and Build Dashboard", use_container_width=True):
        if not research_input.strip():
            st.error("Please enter a valid company name.")
        else:
            with st.spinner(f"Scouring the web for '{research_input}' UPI integrations, growth, and M&A deals..."):
                success, resolved_name = research_agent.research_company(research_input)
                if success:
                    st.success(f"Successfully scoured '{resolved_name}'!")
                    # Rerun to populate the selector with the newly retrieved company
                    st.rerun()
                else:
                    st.error(f"Failed to query information for '{research_input}': {resolved_name}")
                    
    st.markdown("<hr style='border-color: rgba(102,252,241,0.2);'/>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #66fcf1;'>⚙️ Sandbox Controls</h3>", unsafe_allow_html=True)
    if st.button("Clear SQLite Database", use_container_width=True):
        db_manager.clear_database()
        st.warning("Database cleared.")
        st.rerun()
        
    st.markdown("<hr style='border-color: rgba(102,252,241,0.2);'/>", unsafe_allow_html=True)
    # Check for active key dynamically on every Streamlit script execution
    active_key = research_agent.get_api_key()

    if active_key:
        st.markdown("<p style='color:#00ff88; font-weight:600;'>● Gemini Live Connection Active</p>", unsafe_allow_html=True)
        if st.button("🔌 Disconnect / Reset Key", use_container_width=True):
            if "GEMINI_API_KEY" in st.session_state:
                del st.session_state["GEMINI_API_KEY"]
            try:
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                    with open(env_path, "w") as f:
                        for line in lines:
                            if line.startswith("GEMINI_API_KEY="):
                                f.write('GEMINI_API_KEY="REPLACE_THIS_WITH_YOUR_ACTUAL_GEMINI_API_KEY"\n')
                            else:
                                f.write(line)
            except Exception:
                pass
            st.rerun()
    else:
        st.markdown("<p style='color:#ffaa00; font-weight:600;'>▲ Sandbox Mode Active</p>", unsafe_allow_html=True)
        st.info("No API Key detected or placeholder active. Enter your key below or edit the .env file to enable live web scouring.")
        
        # Premium input field in sidebar
        input_key = st.text_input("Enter Gemini API Key", type="password", key="sidebar_api_key", help="Get a free key from https://aistudio.google.com/")
        if input_key.strip():
            st.session_state["GEMINI_API_KEY"] = input_key.strip()
            # Try to write it to .env dynamically to save them manual editing
            try:
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                    with open(env_path, "w") as f:
                        key_written = False
                        for line in lines:
                            if line.startswith("GEMINI_API_KEY="):
                                f.write(f'GEMINI_API_KEY="{input_key.strip()}"\n')
                                key_written = True
                            else:
                                f.write(line)
                        if not key_written:
                            f.write(f'\nGEMINI_API_KEY="{input_key.strip()}"\n')
                else:
                    with open(env_path, "w") as f:
                        f.write(f'GEMINI_API_KEY="{input_key.strip()}"\n')
                st.toast("API Key saved to .env and applied successfully!", icon="🔥")
            except Exception as e:
                st.toast("API Key applied to current session!", icon="⚡")
            st.rerun()

# --- MAIN DASHBOARD FLOW ---

# 1. Company Selection Dropdown
companies_names = [comp["name"] for comp in companies_in_db]

col_header, col_selector = st.columns([2, 1])
with col_header:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 0.5rem;'>
        <h2 style='margin: 0; color: #ffffff;'>⚡ Indian Fintech Scout</h2>
    </div>
    """, unsafe_allow_html=True)
with col_selector:
    # Set default selection to Razorpay if available
    default_idx = companies_names.index("Razorpay") if "Razorpay" in companies_names else 0
    selected_name = st.selectbox("Select Active Fintech Profile", options=companies_names, index=default_idx)

# Get the active company record
active_company = next(comp for comp in companies_in_db if comp["name"] == selected_name)

# Parse leadership
execs_parsed = []
if active_company["executives"]:
    if isinstance(active_company["executives"], str):
        try:
            execs_parsed = json.loads(active_company["executives"])
        except Exception:
            execs_parsed = [{"role": "Executive", "name": active_company["executives"]}]
    else:
        execs_parsed = active_company["executives"]

# --- DYNAMIC HERO PROFILE HEADER ---
st.markdown(f"""
<div class="header-box">
    <span class="header-badge">⭐ {active_company["sector"]}</span>
    <div class="header-title">{active_company["name"]}</div>
    <div class="header-desc"><strong>{active_company["value_prop"]}</strong><br>Scoured via {active_company["source_newsletter"]} on {active_company["extracted_at"][:10]}</div>
</div>
""", unsafe_allow_html=True)

# --- DYNAMIC MAIN KPIs ROW ---
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    arr_val = active_company["sales_revenue"] if active_company["sales_revenue"] else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-name">Sales & Revenue Status</div>
        <div class="metric-num" style="font-size: 1.25rem; padding: 0.4rem 0; color:#ffffff; font-weight:700;">{arr_val}</div>
        <div class="metric-sub">Commercial Performance Metrics</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    cust_val = active_company["customer_count"] if active_company["customer_count"] else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-name">Customer Base & Scale</div>
        <div class="metric-num" style="font-size: 1.25rem; padding: 0.4rem 0; color:#66fcf1; font-weight:700;">{cust_val}</div>
        <div class="metric-sub">Active Users & UPI Traction</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    fund_val = active_company["total_funding_raised"] if active_company["total_funding_raised"] else "N/A"
    stage_val = active_company["funding_stage"] if active_company["funding_stage"] else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-name">Total Capital Raised</div>
        <div class="metric-num">{fund_val}</div>
        <div class="metric-sub">{stage_val} Stage Round</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    emp_val = int(active_company["employee_count"]) if (active_company["employee_count"] and active_company["employee_count"] > 0) else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-name">Team & Org Scale</div>
        <div class="metric-num">{emp_val}</div>
        <div class="metric-sub">Estimated FTE Employees</div>
    </div>
    """, unsafe_allow_html=True)

# --- DETAILED INFORMATION IN MODULAR TABS ---
st.write("")
tab_corp, tab_prod, tab_ma, tab_forecast = st.tabs([
    "📊 Corporate & Leadership", 
    "📦 Products & Technology", 
    "🤝 Transactions & M&A History", 
    "📈 Dynamic Growth Projections"
])

# Tab 1: Corporate & Leadership
with tab_corp:
    col_snap, col_leaders = st.columns(2)
    
    import html
    hq = html.escape(str(active_company["hq_location"])) if active_company["hq_location"] else "Unknown"
    founded = html.escape(str(active_company["founded_year"])) if active_company["founded_year"] else "Unknown"
    sector = html.escape(str(active_company["sector"])) if active_company["sector"] else "Fintech"
    investors = html.escape(str(active_company["key_investors"])) if active_company["key_investors"] else "Information not structured"
    
    with col_snap:
        st.markdown(f"""<div style="background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(102, 252, 241, 0.15); border-radius: 16px; padding: 1.8rem; min-height: 380px; height: 100%; box-sizing: border-box;">
<h4 style="color: #ffffff; margin-top: 0; margin-bottom: 1.5rem; font-weight: 700;">Corporate Snapshot</h4>
<div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05rem; color: #66fcf1; margin-bottom: 0.2rem;">📍 Headquarters</div>
<div style="font-size: 1rem; color: #ffffff; font-weight: 500; margin-bottom: 1rem;">{hq}</div>
<div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05rem; color: #66fcf1; margin-bottom: 0.2rem;">📅 Founded Year</div>
<div style="font-size: 1rem; color: #ffffff; font-weight: 500; margin-bottom: 1rem;">{founded}</div>
<div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05rem; color: #66fcf1; margin-bottom: 0.2rem;">⚡ Focus Sub-Sector</div>
<div style="font-size: 1rem; color: #ffffff; font-weight: 500; margin-bottom: 1rem;">{sector}</div>
<div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05rem; color: #66fcf1; margin-bottom: 0.2rem;">💼 Key Investors & Capital Backers</div>
<div style="font-size: 1rem; color: #ffffff; font-weight: 500; line-height: 1.4;">{investors}</div>
</div>""", unsafe_allow_html=True)
        
    with col_leaders:
        leaders_html = ""
        if execs_parsed:
            for exec_info in execs_parsed:
                name = html.escape(str(exec_info.get("name", "Unknown Officer")))
                role = html.escape(str(exec_info.get("role", "Executive")))
                leaders_html += f"""<div style="background: rgba(11, 12, 16, 0.4); padding: 0.8rem 1.2rem; border-radius: 8px; margin-bottom: 0.8rem; border-left: 3px solid #66fcf1;">
<div style="font-weight: 700; color: #ffffff; font-size: 1.05rem;">{name}</div>
<div style="color: #66fcf1; font-weight: 600; font-size: 0.8rem; text-transform: uppercase;">{role}</div>
</div>"""
        else:
            leaders_html = "<p style='color:#8b949e;'>Key leadership names were not specifically parsed from source documents.</p>"
            
        st.markdown(f"""<div style="background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(102, 252, 241, 0.15); border-radius: 16px; padding: 1.8rem; min-height: 380px; height: 100%; box-sizing: border-box;">
<h4 style="color: #ffffff; margin-top: 0; margin-bottom: 1.5rem; font-weight: 700;">👥 Organizational Structure & Key Officers</h4>
{leaders_html}
</div>""", unsafe_allow_html=True)

# Tab 2: Products & Technology
with tab_prod:
    st.markdown("<div class='section-title'>📦 Core Products & Service Offerings</div>", unsafe_allow_html=True)
    if active_company["products"]:
        st.markdown(f"""
        <div style="background: rgba(22, 27, 34, 0.5); border: 1px solid rgba(102, 252, 241, 0.1); border-radius: 12px; padding: 2rem;">
            <p style="font-size: 1.05rem; line-height: 1.6; color: #c5c6c7;">{active_company["products"]}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Product details are not specifically structured for this company profile yet.")

# Tab 3: Transactions & M&A History
with tab_ma:
    st.markdown("<div class='section-title'>🤝 Past Transactions, Strategic Mergers, & Acquisitions</div>", unsafe_allow_html=True)
    if active_company["transactions_ma"]:
        st.markdown(f"""
        <div style="background: rgba(22, 27, 34, 0.5); border: 1px solid rgba(0, 255, 136, 0.15); border-radius: 12px; padding: 2rem;">
            <p style="font-size: 1.05rem; line-height: 1.6; color: #c5c6c7;">{active_company["transactions_ma"]}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("M&A history and transaction details are not specifically structured for this company profile yet.")

# Tab 4: Dynamic Growth Projections
with tab_forecast:
    st.markdown("<div class='section-title'>📈 Bimonthly Interactive Growth Projections</div>", unsafe_allow_html=True)
    st.write("Simulate bimonthly growth for the active company profile based on customer statistics and growth signals.")
    
    # Establish dynamic starting parameters based on active company
    active_growth_rate = float(active_company["growth_rate_pct"]) if active_company["growth_rate_pct"] else 20.0
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        periods = st.slider("🔮 Forecasting Horizon (Bimonthly Periods)", min_value=1, max_value=12, value=6)
    with col_s2:
        growth_override = st.slider("📊 Adjust Bimonthly Growth Rate (%)", min_value=5, max_value=50, value=int(active_growth_rate))
        
    # Standard compound math starting parameters
    growth_rate = growth_override / 100.0
    
    # Estimate numeric customer starting value
    cust_str = str(active_company["customer_count"]).lower()
    start_customers = 500000 # generic default if parser fails
    
    # Simple multiplier checks
    digits = re.findall(r'\d+\.?\d*', cust_str.replace(",", ""))
    if digits:
        val = float(digits[0])
        if "billion" in cust_str or "b" in cust_str.split():
            start_customers = int(val * 1000000000)
        elif "million" in cust_str or "m" in cust_str.split():
            start_customers = int(val * 1000000)
        else:
            start_customers = int(val) if val > 10 else 500000
            
    # Estimate ARR starting value
    arr_str = str(active_company["sales_revenue"]).lower()
    start_arr = 10000000 # default $10M
    arr_digits = re.findall(r'\d+\.?\d*', arr_str.replace(",", "").replace("$", "").replace("£", ""))
    if arr_digits:
        val = float(arr_digits[0])
        if "billion" in arr_str or "b" in arr_str:
            start_arr = int(val * 1000000000)
        elif "million" in arr_str or "m" in arr_str:
            start_arr = int(val * 1000000)
        else:
            # check if INR or USD scale
            if "cr" in arr_str or "crore" in arr_str:
                # 1 Crore INR ~ 10,000,000 INR
                start_arr = int(val * 10000000)
            else:
                start_arr = int(val) if val > 1000 else 10000000
            
    # Generate projections
    bimonthly_intervals = [f"Current"] + [f"Period {i} ({i*2} mo)" for i in range(1, periods + 1)]
    customer_projections = [start_customers]
    arr_projections = [start_arr]

    for i in range(1, periods + 1):
        next_cust = int(customer_projections[-1] * (1 + growth_rate))
        customer_projections.append(next_cust)
        next_arr = int(arr_projections[-1] * (1 + (growth_rate * 0.95)))
        arr_projections.append(next_arr)

    # Convert to DataFrame
    proj_df = pd.DataFrame({
        "Bimonthly Interval": bimonthly_intervals,
        "Projected Customers": customer_projections,
        "Projected ARR/Sales": arr_projections
    })

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("<h4 style='color: #66fcf1; font-weight: 600;'>User Base Scaling Trend</h4>", unsafe_allow_html=True)
        fig_cust = px.line(
            proj_df,
            x="Bimonthly Interval",
            y="Projected Customers",
            text="Projected Customers",
            markers=True,
            color_discrete_sequence=["#66fcf1"]
        )
        fig_cust.update_traces(textposition="top center", texttemplate="%{y:,.0f}", line=dict(width=3))
        fig_cust.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c5c6c7',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Active Customer Estimate"),
            margin=dict(l=0, r=0, t=20, b=20),
            height=360
        )
        st.plotly_chart(fig_cust, use_container_width=True)

    with col_chart2:
        st.markdown("<h4 style='color: #00ff88; font-weight: 600;'>Revenue/Sales Growth Projections</h4>", unsafe_allow_html=True)
        
        # Decide currency prefix
        curr_symbol = "₹" if ("₹" in str(active_company["sales_revenue"]) or "inr" in str(active_company["hq_location"]).lower() or "india" in str(active_company["hq_location"]).lower()) else "$"
        
        fig_arr = px.bar(
            proj_df,
            x="Bimonthly Interval",
            y="Projected ARR/Sales",
            text="Projected ARR/Sales",
            color="Projected ARR/Sales",
            color_continuous_scale=["#161b22", "#00ff88"]
        )
        fig_arr.update_traces(texttemplate=f"{curr_symbol}%{{text:,.0f}}", textposition="outside")
        fig_arr.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c5c6c7',
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=f"Projected Sales ({curr_symbol})"),
            margin=dict(l=0, r=0, t=20, b=20),
            height=360
        )
        st.plotly_chart(fig_arr, use_container_width=True)

    # Narrative Summary
    st.markdown(f"""
    <div class="forecaster-panel">
        <h4 style="color: #ffffff; margin-top: 0; margin-bottom: 0.8rem; font-weight: 700;">📊 Projected {active_company["name"]} Investment Takeaway</h4>
        <p style="color: #c5c6c7; margin-bottom: 1.5rem;">
            {active_company["growth_description"]}
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; text-align: center;">
            <div style="background: rgba(11, 12, 16, 0.6); padding: 1rem; border-radius: 8px; border: 1px solid rgba(102, 252, 241, 0.2);">
                <div style="font-size: 0.75rem; color: #66fcf1; text-transform: uppercase; font-weight: bold; letter-spacing: 0.05rem;">Forecasted Users</div>
                <div style="font-size: 1.6rem; font-weight: bold; color: #ffffff; margin-top: 0.3rem;">{customer_projections[-1]:,}</div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 0.2rem;">({(customer_projections[-1]/start_customers):.1f}x scaling)</div>
            </div>
            <div style="background: rgba(11, 12, 16, 0.6); padding: 1rem; border-radius: 8px; border: 1px solid rgba(0, 255, 136, 0.2);">
                <div style="font-size: 0.75rem; color: #00ff88; text-transform: uppercase; font-weight: bold; letter-spacing: 0.05rem;">Forecasted Revenue</div>
                <div style="font-size: 1.6rem; font-weight: bold; color: #ffffff; margin-top: 0.3rem;">{curr_symbol}{arr_projections[-1]/1e6:.2f}M</div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 0.2rem;">({(arr_projections[-1]/start_arr):.1f}x multiplier)</div>
            </div>
            <div style="background: rgba(11, 12, 16, 0.6); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="font-size: 0.75rem; color: #ffffff; text-transform: uppercase; font-weight: bold; letter-spacing: 0.05rem;">Scout Cycles</div>
                <div style="font-size: 1.6rem; font-weight: bold; color: #ffffff; margin-top: 0.3rem;">{periods} bimonthly rounds</div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 0.2rem;">({periods * 2} calendar months)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer details
st.markdown("<hr style='border-color: rgba(102, 252, 241, 0.15); margin-top: 3rem;'/>", unsafe_allow_html=True)
st.caption("Investment Banking Indian & Global Fintech Scouting Portal | Powered by Google Gemini and SQLite.")
