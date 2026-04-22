import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
from datetime import datetime
from database import init_db, save_ticket, load_all_tickets, update_ticket_status
from ml_engine import analyze_complaint

# Initialize System
init_db()

# ==========================================
# 🌍 NAIROBI GEODATA
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
# 🖥️ GLOBAL SETTINGS & DATA
# ==========================================
st.set_page_config(page_title="Sikika AI | Nairobi", layout="wide")

# Fetch and Prepare Data
st.session_state.tickets = load_all_tickets()
df = pd.DataFrame(st.session_state.tickets)

if not df.empty:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

st.title("🛣️ Sikika AI - Ministry of Roads")
# 1. UPDATED TABS: Added 'Track My Grievance'
tab_form, tab_track, tab_analytics, tab_admin = st.tabs([
    "📝 Citizen Reporting Portal", 
    "🔍 Track My Grievance", 
    "📊 Strategic Analytics", 
    "🔐 Admin Dashboard"
])

# --- TAB 1: CITIZEN REPORTING ---
with tab_form:
    st.subheader("Submit Official Road Grievance")
    with st.form("grievance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*")
            email = st.text_input("Email Address") 
            number = st.text_input("Phone Number*")
        with col2:
            selected_sub = st.selectbox("Sub-county*", options=sub_counties_list)
            wards_list = [w.title() for sc in NAIROBI_DATA[0]["sub_counties"] if sc["subcounty_name"].title() == selected_sub for w in sc["wards"]]
            selected_ward = st.selectbox("Ward*", options=wards_list)
            landmark = st.text_input("Nearest Landmark")
        
        complaint = st.text_area("Describe the Infrastructure Issue*")
        submitted = st.form_submit_button("Submit Grievance")
        
        if submitted:
            if name and number and complaint:
                with st.spinner('AI Engine processing...'):
                    complaint_type, priority = analyze_complaint(complaint)
                    ticket_id = f"NRB-{random.randint(100000, 999999)}"
                    new_ticket = {
                        "Ticket ID": ticket_id, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Name": name, "Email": email, "Phone": number, "Sub-county": selected_sub,
                        "Ward": selected_ward, "Landmark": landmark, "complaint_text": complaint,
                        "Category": complaint_type.title(), "AI Priority": priority, "Status": "Open", "Hotspot": "No"
                    }
                    save_ticket(new_ticket)
                    st.rerun() 
                st.success(f"✅ Ticket Raised: **{ticket_id}**")

# --- NEW TAB 2: TRACK MY GRIEVANCE ---
with tab_track:
    st.subheader("🔍 Real-Time Status Tracking")
    st.markdown("Enter your unique Ticket ID to see the official progress of your report.")
    
    # 1. SEARCH INTERFACE
    track_col1, track_col2 = st.columns([2, 1])
    
    with track_col1:
        search_id = st.text_input("Ticket ID", placeholder="e.g., NRB-123456", label_visibility="collapsed")
    
    with track_col2:
        # THE NEW TRACK BUTTON
        track_btn = st.button("Track Ticket", type="primary", use_container_width=True)
    
    # 2. TRIGGER SEARCH LOGIC
    if track_btn:
        if search_id:
            # Search logic (Case-insensitive)
            result = df[df['Ticket ID'].str.upper() == search_id.strip().upper()]
            
            if not result.empty:
                ticket = result.iloc[0]
                status = ticket['Status']
                
                st.divider()
                
                # --- TICKET STATUS CARD ---
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    # Visual status indicator based on DB
                    if "Open" in status:
                        st.warning(f"Current State: {status}")
                    elif "In Progress" in status:
                        st.info(f"Current State: {status}")
                    else:
                        st.success(f"Current State: {status}")
                    
                    st.metric("AI Assigned Priority", ticket['AI Priority'])
                
            with res_col2:
                st.markdown(f"### Ticket Details")
                st.write(f"**Reporter:** {ticket['Name']}")
                st.write(f"**Issue Category:** {ticket['Category']}")
                st.write(f"**Location:** {ticket['Ward']}, {ticket['Sub-county']}")
                st.write(f"**Logged On:** {ticket['Timestamp'].strftime('%d %b %Y, %H:%M')}")
                
            st.divider()

            # --- PROGRESS TIMELINE (Logic-driven from DB) ---
            st.markdown("##### 🛤️ Infrastructure Resolution Timeline")
            
            # Step 1: Always completed if ticket exists
            st.write("✅ **Grievance Received:** The Sikika AI Engine has successfully logged and prioritized this issue.")
            
            # Step 2: Completed if "In Progress" or "Resolved"
            if status in ["In Progress", "Resolved"]:
                st.write("✅ **Technical Dispatch:** A regional maintenance team has been assigned to the landmark.")
            else:
                st.write("⬜ **Technical Dispatch:** Awaiting team assignment based on priority queue.")
                
            # Step 3: Completed only if "Resolved"
            if status == "Resolved":
                st.write("✅ **Final Resolution:** Work completed. The infrastructure issue has been addressed and verified.")
            else:
                st.write("⬜ **Final Resolution:** Verification and closure pending.")

        else:
            st.error("Ticket ID not found. Please ensure the ID matches the one provided at submission.")
    elif not track_btn and search_id:
        st.info("Click 'Track Ticket' to retrieve the latest status.")

# --- TAB 2: STRATEGIC ANALYTICS ---
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

# --- TAB 3: ADMIN DASHBOARD ---
with tab_admin:
    st.subheader("🔐 Grievance Management Dashboard")
    
    if not df.empty:
        # 1. SEARCH LOG
        search = st.text_input("🔍 Filter Master Archive by ID, Name, or Landmark")
        
        admin_df = df.copy()
        if search:
            admin_df = admin_df[
                admin_df['Ticket ID'].str.contains(search, case=False, na=False) | 
                admin_df['Name'].str.contains(search, case=False, na=False) | 
                admin_df['Landmark'].str.contains(search, case=False, na=False)
            ]
        
        # 2. MASTER TABLE
        st.dataframe(admin_df.sort_values(by="Timestamp", ascending=False), use_container_width=True, hide_index=True)
        
        # 📥 CSV DOWNLOAD (REPOSITIONED BELOW TABLE)
        csv_data = admin_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export View to CSV",
            data=csv_data,
            file_name=f"ministry_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )

        st.divider()

        # 3. ACTION CENTER: STATUS UPDATES
        st.subheader("📝 Resolution Action Center")
        with st.expander("Update Ticket Status", expanded=True):
            search_resolve = st.text_input("Search Ticket ID to resolve:", key="resolve_search")
            
            if search_resolve:
                opts = admin_df[admin_df['Ticket ID'].str.contains(search_resolve, case=False) | admin_df['Name'].str.contains(search_resolve, case=False)]
            else:
                opts = admin_df.sort_values(by="Timestamp", ascending=False).head(10)

            if not opts.empty:
                t_id = st.selectbox("Select Target Ticket ID", options=opts['Ticket ID'].tolist())
                sel_row = df[df['Ticket ID'] == t_id].iloc[0]
                
                st.info(f"**Editing Ticket:** {t_id} | **Citizen:** {sel_row['Name']} | **Current Status:** {sel_row['Status']}")
                
                c_u1, c_u2 = st.columns(2)
                with c_u1:
                    # RESTRICTED STATUS OPTIONS
                    status_options = ["Open", "In Progress", "Resolved"]
                    n_stat = st.selectbox("New Resolution Status", options=status_options)
                with c_u2:
                    st.text_area("Resolution Feedback (Internal/External)")
                
                if st.button("Confirm Update", type="primary", use_container_width=True):
                    update_ticket_status(t_id, n_stat)
                    st.success(f"Status for {t_id} updated to {n_stat}!")
                    st.rerun()
            else:
                st.warning("No records match your search criteria.")
    else:
        st.info("System archive is empty.")