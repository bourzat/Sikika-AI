import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
from datetime import datetime
from database import init_db, save_ticket, load_all_tickets, update_ticket_status
from ml_engine import analyze_complaint

# ==========================================
# 🖥️ GLOBAL SETTINGS (MUST BE FIRST)
# ==========================================
st.set_page_config(page_title="Sikika AI | Nairobi", layout="wide")

# ==========================================
# 💾 DATA INITIALIZATION
# ==========================================
init_db() # Ensures the table exists, even if empty

# Fetch fresh data from DB on every run/refresh
st.session_state.tickets = load_all_tickets()
df = pd.DataFrame(st.session_state.tickets)

if not df.empty:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# ==========================================
# 🌍 3. NAIROBI GEODATA
# ==========================================
NAIROBI_DATA = [
    {
        "county_name": "NAIROBI",
        "sub_counties": [
            {"subcounty_name": "westlands", "wards": ["kitisuru", "parklands/highridge", "karura", "kangemi", "mountain view"]},
            {"subcounty_name": "dagoretti north", "wards": ["kilimani", "kawangware", "gatina", "kileleshwa", "kabiro"]},
            {"subcounty_name": "dagoretti south", "wards": ["mutuini", "ngando", "riruta", "uthiru/ruthimitu", "waithaka"]},
            {"subcounty_name": "langata", "wards": ["karen", "nairobi west", "mugumo-ini", "south-c", "nyayo highrise"]},
            {"subcounty_name": "kibra", "wards": ["laini saba", "lindi", "makina", "woodley/kenyatta golf", "sarangombe"]},
            {"subcounty_name": "roysambu", "wards": ["githurai", "kahawa west", "zimmerman", "roysambu", "kahawa"]},
            {"subcounty_name": "kasarani", "wards": ["claycity", "mwiki", "kasarani", "njiru", "ruai"]},
            {"subcounty_name": "ruaraka", "wards": ["baba dogo", "utalii", "mathare north", "lucky summer", "korogocho"]},
            {"subcounty_name": "embakasi south", "wards": ["imara daima", "kwa njenga", "kwa reuben", "pipeline", "kware"]},
            {"subcounty_name": "embakasi north", "wards": ["kariobangi north", "dandora area i", "dandora area ii", "dandora area iii", "dandora area iv"]},
            {"subcounty_name": "embakasi central", "wards": ["kayole north", "kayole central", "kayole south", "komarock", "matopeni"]},
            {"subcounty_name": "embakasi east", "wards": ["upper savannah", "lower savannah", "embakasi", "utawala", "mihango"]},
            {"subcounty_name": "embakasi west", "wards": ["umoja i", "umoja ii", "mowlem", "kariobangi south"]},
            {"subcounty_name": "makadara", "wards": ["makongeni", "maringo/hamza", "harambee", "viwandani"]},
            {"subcounty_name": "kamukunji", "wards": ["pumwani", "eastleigh north", "eastleigh south", "airbase", "california"]},
            {"subcounty_name": "starehe", "wards": ["nairobi central", "ngara", "ziwani/kariokor", "pangani", "landimawe", "nairobi south"]},
            {"subcounty_name": "mathare", "wards": ["hospital", "mabatini", "huruma", "ngei", "mlango kubwa", "kiamaiko"]}
        ]
    }
]
sub_counties_list = [sc["subcounty_name"].title() for sc in NAIROBI_DATA[0]["sub_counties"]]

# ==========================================
# 🏗️ 4. UI LAYOUT
# ==========================================
st.title("🛣️ Sikika AI - Ministry of Roads")

tab_form, tab_track, tab_analytics, tab_admin, tab_dev = st.tabs([
    "📝 Citizen Reporting Portal", 
    "🔍 Track My Grievance", 
    "📊 Strategic Analytics", 
    "🔐 Admin Dashboard",
    "💻 Developer Portal"
])


# --- TAB 1: CITIZEN REPORTING ---
with tab_form:
    st.subheader("Submit Official Road Grievance")

    # This creates the single "box" container you see in your UI
    with st.container(border=True):
        st.markdown("##### 📋 Grievance Details")
        
        # Split into two main vertical columns
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Column 1: Personal Info
            name = st.text_input("Full Name*", placeholder="e.g., John Doe")
            email = st.text_input("Email Address", placeholder="e.g., john@example.com")
            number = st.text_input("Phone Number*", placeholder="e.g., 0712345678")
            
        with col_right:
            # Column 2: Location Info (Reactive!)
            selected_sub = st.selectbox("Sub-county*", options=sub_counties_list)
            
            # Logic for dynamic Ward list
            wards_list = [
                w.title() for sc in NAIROBI_DATA[0]["sub_counties"] 
                if sc["subcounty_name"].title() == selected_sub 
                for w in sc["wards"]
            ]
            selected_ward = st.selectbox("Ward*", options=wards_list)
            landmark = st.text_input("Nearest Landmark", placeholder="e.g., Opposite Shell Station")

        # Bottom section: The text area spans the full width
        complaint = st.text_area("Describe the Infrastructure Issue*", height=150)
        
        # Use a regular button instead of a form_submit_button to allow reactivity
        if st.button("Submit Grievance", type="primary", use_container_width=True):
            if name and number and complaint:
                with st.spinner('AI Engine processing...'):
                    # ML Engine Logic
                    complaint_type, priority = analyze_complaint(complaint)
                    ticket_id = f"NRB-{random.randint(100000, 999999)}"
                    
                    # Save to DB
                    new_ticket = {
                        "Ticket ID": ticket_id, 
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Name": name, "Email": email, "Phone": number, 
                        "Sub-county": selected_sub, "Ward": selected_ward, 
                        "Landmark": landmark, "complaint_text": complaint,
                        "Category": complaint_type.title(), "AI Priority": priority, 
                        "Status": "Open", "Hotspot": "No"
                    }
                    save_ticket(new_ticket)
                    
                    # Force refresh of session data
                    st.session_state.tickets = load_all_tickets()
                
                st.success(f"✅ Grievance Logged! Ticket ID: **{ticket_id}**")

                # THE PRO-TIP BOX
                st.info(f"💡 **Pro-Tip:** Copy and save your Ticket ID to track progress in the 'Track My Grievance' tab.")
            else:
                st.error("Please fill in all required fields (*) before submitting.")

# --- TAB 2: TRACK MY GRIEVANCE ---
# --- TAB 2: TRACK MY GRIEVANCE ---
with tab_track:
    st.subheader("🔍 Track Your Grievance Status")
    
    # 1. THE FIX: Explicitly convert to DataFrame to avoid TypeError
    raw_tickets = st.session_state.get('tickets', load_all_tickets())
    tracking_df = pd.DataFrame(raw_tickets)
    
    # Unified Container for the search and result
    with st.container(border=True):
        st.markdown("##### 🔍 Enter Details")
        
        # Search input and Button on the same line or stacked
        search_id = st.text_input("Ticket ID", placeholder="e.g., NRB-123456", key="tracking_search_bar")
        track_clicked = st.button("Track Status", type="primary", use_container_width=True)
        
        # Only process if they actually clicked the button or hit enter
        if search_id and track_clicked:
            clean_id = search_id.strip()
            
            # Check if the dataframe is empty first
            if not tracking_df.empty and 'Ticket ID' in tracking_df.columns:
                result = tracking_df[tracking_df['Ticket ID'] == clean_id]
                
                if not result.empty:
                    ticket = result.iloc[0]
                    st.divider()
                    
                    # Columns for the status display
                    res_col1, res_col2 = st.columns(2) 
                    
                    with res_col1:
                        st.metric("Current Status", ticket['Status'])
                        st.write(f"**Category:** {ticket['Category']}")
                        st.write(f"**Logged on:** {ticket['Timestamp']}")
                        
                    with res_col2:
                        st.write(f"**Sub-county:** {ticket['Sub-county']}")
                        st.write(f"**Ward:** {ticket['Ward']}")
                        st.write(f"**Landmark:** {ticket['Landmark']}")
                        
                    st.divider()
                    st.markdown(f"**Citizen Complaint:**\n> {ticket['complaint_text']}")
                    
                    # Show resolution feedback if it exists
                    if 'Feedback' in ticket and pd.notna(ticket['Feedback']) and ticket['Feedback'] != "":
                        st.info(f"**Ministry Feedback:**\n\n{ticket['Feedback']}")
                else:
                    st.error("Ticket ID not found. Please check the ID and try again.")
            else:
                st.warning("The database is currently empty. Raise a grievance first!")
            
# --- TAB 3: STRATEGIC ANALYTICS ---
with tab_analytics:
    if not df.empty:
        st.markdown("#### 🔍 Filter Operational Intelligence")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            f_cat = st.selectbox("Infrastructure Category:", ["All Issues"] + sorted(list(df['Category'].unique())))
        with f_col2:
            f_sub = st.selectbox("Sub-county Jurisdiction:", ["All Sub-counties"] + sorted(list(df['Sub-county'].unique())))

        f_df = df.copy()
        if f_cat != "All Issues": f_df = f_df[f_df['Category'] == f_cat]
        if f_sub != "All Sub-counties": f_df = f_df[f_df['Sub-county'] == f_sub]
            
        st.divider()

        # KPIs showing Full Breakdown
        m_tot, m_crit, m_high, m_med, m_low = st.columns(5)
        m_tot.metric("Total Filtered", len(f_df))
        m_crit.metric("🔴 Critical", len(f_df[f_df["AI Priority"] == "Critical"]))
        m_high.metric("🟠 High", len(f_df[f_df["AI Priority"] == "High"]))
        m_med.metric("🟡 Medium", len(f_df[f_df["AI Priority"] == "Medium"]))
        m_low.metric("🟢 Low", len(f_df[f_df["AI Priority"] == "Low"]))
        
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Geographical Incident Distribution (Top 10)")
            tw = f_df['Ward'].value_counts().nlargest(10).reset_index()
            tw.columns = ['Ward', 'Count']
            st.plotly_chart(px.bar(tw, x='Count', y='Ward', orientation='h', color='Count', color_continuous_scale='Reds').update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10,b=10)), use_container_width=True)
        with c2:
            st.markdown("##### Infrastructure Failure Frequency")
            ti = f_df['Category'].value_counts().nlargest(10).reset_index()
            ti.columns = ['Category', 'Count']
            st.plotly_chart(px.bar(ti, x='Count', y='Category', orientation='h', color='Count', color_continuous_scale='Oranges').update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10,b=10)), use_container_width=True)

        st.divider()

        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown("##### 🚨 Regional Risk Intensity Matrix")
            rm = f_df.groupby(['Sub-county', 'AI Priority']).size().unstack(fill_value=0)
            po = [p for p in ["Critical", "High", "Medium", "Low"] if p in rm.columns]
            st.plotly_chart(px.imshow(rm[po], text_auto=True, color_continuous_scale="Reds", aspect="auto").update_layout(margin=dict(t=10,b=10), coloraxis_showscale=False), use_container_width=True)
        with c4:
            st.markdown("##### 📍 High-Priority Hotspots")
            hot = f_df[f_df['AI Priority'].isin(['Critical', 'High'])]
            if not hot.empty:
                hs = hot['Ward'].value_counts().nlargest(5).reset_index()
                hs.columns = ['WardName', 'ReportCount'] 
                for _, row in hs.iterrows(): st.error(f"**{row['WardName']}**: {row['ReportCount']} Reports")
            else: st.success("No emergency hotspots detected.")
    else:
        st.info("No data available for analysis.")


# --- TAB 4: ADMIN DASHBOARD ---
with tab_admin:
    
    if not df.empty:
        # Create a placeholder at the very top for notifications
        admin_notif = st.empty()

        # --- 1. ACTION CENTER ---
        st.subheader("📝 Resolution Action Center")
        with st.expander("Update Ticket Status", expanded=True):
            search_resolve = st.text_input("Search Ticket ID to resolve:", key="resolve_search_input")
            
            if search_resolve:
                opts = df[df['Ticket ID'].str.contains(search_resolve, case=False) | df['Name'].str.contains(search_resolve, case=False)]
            else:
                opts = df.sort_values(by="Timestamp", ascending=False).head(10)

            if not opts.empty:
                t_id = st.selectbox("Select Target Ticket ID", options=opts['Ticket ID'].tolist(), key="target_ticket_id")
                sel_row = df[df['Ticket ID'] == t_id].iloc[0]
                
                st.info(f"**Editing Ticket:** {t_id} | **Citizen:** {sel_row['Name']} | **Current Status:** {sel_row['Status']}")
                
                c_u1, c_u2 = st.columns(2)
                with c_u1:
                    status_options = ["Open", "In Progress", "Resolved"]
                    n_stat = st.selectbox("New Resolution Status", options=status_options, key="new_status_dropdown")
                with c_u2:
                    feedback_text = st.text_area("Resolution Feedback (Internal/External)", key="feedback_textarea")
                
# --- THE CORRECTED BUTTON BLOCK ---
                if st.button("Confirm Update", type="primary", use_container_width=True, key="confirm_update_btn"):
                    import time
                    from notifications import send_citizen_email
                    
                    # 1. Capture the email specifically from the current selection
                    # This ensures it's the real citizen email, not yours!
                    target_email = str(sel_row['Email']).strip()
                    
                    # 2. Update DB - Passing feedback_text so it's saved forever
                    update_ticket_status(t_id, n_stat, feedback_text)
                    
                    # 3. Send Email notification
                    email_sent = send_citizen_email(target_email, t_id, n_stat, feedback_text)
                    
                    # 4. Show success message in the placeholder
                    if email_sent:
                        admin_notif.success(f"✅ Status updated and notification sent to: {target_email}")
                    else:
                        admin_notif.warning(f"✅ Status updated, but email to {target_email} failed.")
                    
                    # 5. Short pause to let them read the success, then refresh
                    time.sleep(2) 
                    st.rerun()

        st.divider()

        # --- 2. MASTER ARCHIVE ---
        st.subheader("🗄️ Master Database Archive")
        search = st.text_input("🔍 Filter Master Archive by ID, Name, or Landmark", key="master_archive_search")
        
        admin_df = df.copy()
        if search:
            admin_df = admin_df[
                admin_df['Ticket ID'].str.contains(search, case=False, na=False) | 
                admin_df['Name'].str.contains(search, case=False, na=False) | 
                admin_df['Landmark'].str.contains(search, case=False, na=False)
            ]
        
        st.dataframe(admin_df.sort_values(by="Timestamp", ascending=False), use_container_width=True, hide_index=True)
        
        # CSV Section
        st.markdown("---")
        c_down1, c_down2 = st.columns([1, 2])
        with c_down1:
            csv_data = admin_df.to_csv(index=False).encode('utf-8')
            if st.download_button(
                label="📥 Export View to CSV",
                data=csv_data,
                file_name=f"ministry_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                key="csv_export_btn"
            ):
                # Note: Streamlit won't show this message UNTIL the next rerun 
                # because the download button is a browser-level event.
                st.toast("CSV Download Started!", icon="📥")
                
    else:
        st.info("System archive is empty.")

# --- TAB 5: DEVELOPER PORTAL (NEW!) ---
with tab_dev:
    st.subheader("💳 Enterprise API Access")
    st.markdown("Purchase a live API key via M-Pesa to stream Sikika Risk Intelligence directly to your logistics platforms.")
    
    dev_c1, dev_c2, dev_c3 = st.columns(3)
    with dev_c1:
        company_name = st.text_input("Company Name", placeholder="e.g., Sendy Logistics")
    with dev_c2:
        billing_phone = st.text_input("M-Pesa Billing Phone", placeholder="07XXXXXXXX")
    with dev_c3:
        tier = st.selectbox("API Subscription Tier", ["Basic (1 KES/mo)", "Pro (2 KES/mo)", "Enterprise (5 KES/mo)"])
        
    if st.button("Generate Invoice & Pay via M-Pesa", type="primary"):
        if company_name and billing_phone:
            from mpesa import trigger_stk
            import uuid
            import time
            
            amount = int(tier.split("(")[1].split(" ")[0])
            
            with st.spinner("Connecting to Safaricom Daraja API..."):
                response = trigger_stk(billing_phone, amount)
                
                if response and response.get("ResponseCode") == "0":
                    st.success(f"✅ STK Push successfully triggered on {billing_phone}.")
                    
                    # --- THE HACKATHON DELAY (Simulates webhook callback) ---
                    with st.spinner("⏳ Awaiting M-Pesa payment confirmation... (Please enter your PIN)"):
                        time.sleep(8) # Gives you 8 seconds to type your PIN during the live pitch!
                    
                    # Generate Fake Live Key 
                    fake_api_key = f"sk_live_{uuid.uuid4().hex[:24]}"
                    st.balloons()
                    st.success("**✅ Payment Verified! Your Developer Account is now active.**")
                    st.info(f"**Your Live API Key:** `{fake_api_key}`")
                    
                    # --- NEW: INSTANT DOCUMENTATION WITH EXPLANATIONS ---
                    st.divider()
                    st.markdown("### 📚 API Quick Start Guide")
                    st.markdown("Inject your new API key into the headers to authenticate your requests.")
                    
                    st.markdown("#### 1. Fetch Risk Intelligence (Monetization Layer)")
                    st.markdown("> **What it does:** Returns aggregated risk scores, resolution rates, and regional hazard indexes.\n> **Use Case:** Logistics companies (e.g., Glovo, Sendy) use this to route drivers away from suspension-killing potholes, or insurance firms use it for risk modeling.")
                    st.code(f"""
import requests

url = "http://127.0.0.1:8000/v1/analytics/risk-intelligence"
headers = {{"Authorization": "Bearer {fake_api_key}"}}

response = requests.get(url, headers=headers)
print(response.json())
                    """, language="python")
                    
                    st.markdown("#### 2. Fetch Master Grievance Feed (Integration Layer)")
                    st.markdown("> **What it does:** Pulls the raw, real-time database of reported road issues, filterable by location and status.\n> **Use Case:** Government portals like eCitizen, or local ward administrators pulling exact ticket data into their own internal dashboards.")
                    st.code(f"""
curl -X 'GET' \\
  'http://127.0.0.1:8000/v1/grievances?status=Open' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer {fake_api_key}'
                    """, language="bash")
                    
                    st.caption("🔗 Want to test it live in your browser? Open the interactive Swagger UI at `http://127.0.0.1:8000/docs`")
                    
                else:
                    st.error(f"❌ Transaction Failed: {response.get('errorMessage', 'Check Daraja Credentials')}")
        else:
            st.warning("Please enter a valid Company Name and M-Pesa Phone Number.")
