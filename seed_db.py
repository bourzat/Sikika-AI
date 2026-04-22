import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, save_ticket

# --- MOCK DATA LIBRARIES ---
NAMES = ["John Kamau", "Mary Atieno", "David Omondi", "Faith Wanjiku", "Samuel Otieno", "Mercy Chepngetich", "Peter Mutua", "Sarah Nyambura", "James Okoth", "Esther Wairimu"]
ISSUES = [
    ("Pothole", "Large pothole near the stage, causing traffic."),
    ("Street Light", "Street lights are not working, very dark at night."),
    ("Drainage", "Blocked drainage causing flooding after the rains."),
    ("Road Marking", "Faded zebra crossing, very dangerous for pedestrians."),
    ("Illegal Bumps", "Someone put unofficial soil bumps on this road."),
    ("Bridge Repair", "Small crack on the pedestrian bridge, needs checking.")
]
SUB_COUNTIES = {
    "Westlands": ["Kitisuru", "Parklands/Highridge", "Karura", "Kangemi", "Mountain View"],
    "Kasarani": ["Claycity", "Mwiki", "Kasarani", "Njiru", "Ruai"],
    "Starehe": ["Nairobi Central", "Ngara", "Pangani", "Landimawe", "Nairobi South"],
    "Langata": ["Karen", "South-C", "Nairobi West", "Mugumo-ini"],
    "Kibra": ["Makina", "Laini Saba", "Lindi", "Sarangombe"]
}
PRIORITIES = ["Critical", "High", "Medium", "Low"]
STATUSES = ["Open", "In Progress", "Resolved"]

def seed_database(n=2000):
    print(f"🚀 Initializing Database and Seeding {n} Records...")
    init_db()
    
    for i in range(n):
        # Generate Random Logic
        sub = random.choice(list(SUB_COUNTIES.keys()))
        ward = random.choice(SUB_COUNTIES[sub])
        cat, base_desc = random.choice(ISSUES)
        
        # Randomize the date over the last 30 days
        days_ago = random.randint(0, 30)
        timestamp = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M")
        
        ticket = {
            "Ticket ID": f"NRB-{random.randint(100000, 999999)}",
            "Timestamp": timestamp,
            "Name": random.choice(NAMES),
            "Email": f"user{random.randint(1, 999)}@gmail.com",
            "Phone": f"07{random.randint(10, 99)}{random.randint(100000, 999999)}",
            "Sub-county": sub,
            "Ward": ward,
            "Landmark": f"Near {random.choice(['Shell', 'Total', 'KCB Bank', 'Police Post', 'Supermarket'])}",
            "complaint_text": f"{base_desc} Specific spot: {ward} area.",
            "Category": cat,
            "AI Priority": random.choice(PRIORITIES),
            "Status": random.choice(STATUSES),
            "Hotspot": "No"
        }
        
        save_ticket(ticket)
        
        if (i + 1) % 500 == 0:
            print(f"✅ {i + 1} records injected...")

if __name__ == "__main__":
    # Wipe old DB if you want a fresh start, otherwise it appends
    import os
    if os.path.exists("grievances.db"):
        os.remove("grievances.db")
    
    seed_database(2000)
    print("✨ Database ready for the Strategic Analytics demo!")