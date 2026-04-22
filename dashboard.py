import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
from datetime import datetime
from database import init_db, save_ticket, load_all_tickets
from ml_engine import analyze_complaint, detect_clusters

# Initialize Database
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
# 🖥️ STREAMLIT SETTINGS
# ==========================================
st.set_page_config(page_title="Nairobi Roads Tracker", layout="wide")
if 'tickets' not in st.session_state:
    st.session_state.tickets = load_all_tickets()

st.title("🛣️ Ministry of Roads - AI Grievance Tracker")
tab_form, tab_admin = st.tabs(["📝 Report an Issue", "📊 Admin Dashboard"])

# --- TAB 1: REPORTING FORM ---
with tab_form:
    st.subheader("Submit a New Grievance")
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
        
        complaint = st.text_area("Describe the Road Issue*")
        submitted = st.form_submit_button("Submit Ticket")
        
        if submitted:
            if name and number and complaint:
                with st.spinner('Analyzing...'):
                    complaint_type, priority = analyze_complaint(complaint)
                    status = "Escalated 🔴" if priority == "Critical" else "Open 🟡" if priority == "Medium" else "Logged 🟢"
                    ticket_id = f"MOR-{random.randint(100000, 999999)}"
                    
                    new_ticket = {
                        "Ticket ID": ticket_id, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Name": name, "Email": email, "Phone": number, "Sub-county": selected_sub,
                        "Ward": selected_ward, "Landmark": landmark, "complaint_text": complaint,
                        "Category": complaint_type.title(), "AI Priority": priority, "Status": status, "Hotspot": "No"
                    }
                    
                    save_ticket(new_ticket)
                    st.session_state.tickets = load_all_tickets() # Refresh from DB
                st.success(f"✅ Ticket Raised: **{ticket_id}**")

# --- TAB 2: ADMIN DASHBOARD ---
with tab_admin:
    if st.session_state.tickets:
        df = pd.DataFrame(st.session_state.tickets)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # 🎛️ COMMAND CENTER FILTERS
        st.markdown("### 🎛️ Command Center Controls")
        filter_col, _ = st.columns([1, 2])
        with filter_col:
            issue_list = ["All Issues"] + sorted(list(df['Category'].unique()))
            selected_issue = st.selectbox("Filter Dashboard by Infrastructure Issue:", issue_list)
        
        filtered_df = df if selected_issue == "All Issues" else df[df['Category'] == selected_issue]
        st.divider()

        # 📊 DYNAMIC KPIs
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tickets (Filtered)", len(filtered_df))
        m2.metric("Critical Emergencies", len(filtered_df[filtered_df["AI Priority"] == "Critical"]))
        m3.metric("Medium/Low Issues", len(filtered_df[filtered_df["AI Priority"].isin(["Medium", "Low"])]))
        m4.metric("Escalated to Dispatch", len(filtered_df[filtered_df["Status"] == "Escalated 🔴"]))
        
        # 📈 ROW 1: TOP 10 BREAKDOWNS
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Top 10 Most Affected Wards")
            top_wards = filtered_df['Ward'].value_counts().nlargest(10).reset_index()
            top_wards.columns = ['Ward', 'Count']
            st.plotly_chart(px.bar(top_wards, x='Count', y='Ward', orientation='h', color='Count', color_continuous_scale='Reds').update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10,b=10)), use_container_width=True)
        
        with c2:
            st.markdown("##### Top Infrastructure Failures")
            top_issues = filtered_df['Category'].value_counts().nlargest(10).reset_index()
            top_issues.columns = ['Category', 'Count']
            st.plotly_chart(px.bar(top_issues, x='Count', y='Category', orientation='h', color='Count', color_continuous_scale='Oranges').update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, margin=dict(t=10,b=10)), use_container_width=True)

        st.divider()

        # 📈 ROW 2: RISK MATRIX & HOTSPOT LIST
        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown("##### 🚨 Regional Risk Matrix")
            risk_matrix = filtered_df.groupby(['Sub-county', 'AI Priority']).size().unstack(fill_value=0)
            available = [p for p in ["Critical", "High", "Medium", "Low"] if p in risk_matrix.columns]
            risk_matrix = risk_matrix[available]
            st.plotly_chart(px.imshow(risk_matrix, text_auto=True, color_continuous_scale="Reds", aspect="auto").update_layout(margin=dict(t=10,b=10), coloraxis_showscale=False), use_container_width=True)

        with c4:
            st.markdown("##### 📍 Priority Hotspot List")
            # Get the top 5 specific Wards with Critical/High issues
            hot_df = filtered_df[filtered_df['AI Priority'].isin(['Critical', 'High'])]
            
            if not hot_df.empty:
                # Explicitly naming columns to avoid the KeyError
                hotspots = hot_df['Ward'].value_counts().nlargest(5).reset_index()
                hotspots.columns = ['WardName', 'ReportCount'] 
                
                for _, row in hotspots.iterrows():
                    st.error(f"**{row['WardName']}**: {row['ReportCount']} Emergency Reports")
            else:
                st.success("No high-priority clusters detected.")

        st.divider()

        # 📋 ACTIONABLE LOG
        st.markdown("##### 📋 Actionable Ticket Log")
        def color_prio(val):
            color = '#FF4B4B' if val == 'Critical' else '#FACA2B' if val == 'Medium' else '#00CC96'
            return f'color: {color}; font-weight: bold'
        st.dataframe(filtered_df.drop(columns=['Timestamp']).style.map(color_prio, subset=['AI Priority']), use_container_width=True, hide_index=True)

    else:
        st.info("No data available.")