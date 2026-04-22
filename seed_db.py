import sqlite3
import random
from datetime import datetime, timedelta
from database import init_db, save_ticket

# Realistic Nairobi Geodata from your previous version
LOCATIONS = [
    ("Westlands", "Parklands/Highridge", "Aga Khan Hospital"),
    ("Westlands", "Karura", "Village Market"),
    ("Langata", "South-C", "South C Mosque"),
    ("Langata", "Karen", "Karen Crossroads"),
    ("Kibra", "Makina", "Kibera Law Courts"),
    ("Kasarani", "Kasarani", "TRM Mall"),
    ("Starehe", "Nairobi Central", "Kencom"),
    ("Embakasi East", "Utawala", "Eastern Bypass"),
    ("Kamukunji", "Eastleigh North", "First Avenue")
]

# Complaints merged with your new 3-status logic (Open, In Progress, Resolved)
COMPLAINTS = [
    ("Massive pothole causing traffic buildup and damaging tires.", "Potholes & Road Surface", "Medium"),
    ("Someone stole the manhole cover on the pavement, huge hazard.", "Vandalism & Streetlights", "Medium"),
    ("Traffic lights at the intersection have been dead since morning.", "Traffic Signals & Signs", "Critical"),
    ("The drainage is completely blocked, road is flooded and impassable.", "Drainage & Flooding", "Critical"),
    ("Matatus are overlapping heavily on the pedestrian walkway.", "Traffic Violations", "Medium"),
    ("A stalled lorry has blocked the left lane causing a huge jam.", "Road Obstructions", "Medium"),
    ("Terrible accident between a bus and a personal car, road completely blocked.", "Accidents & Collisions", "Critical"),
    ("They built a new speed bump but didn't paint it, cars are flying.", "Unmarked Bumps", "High"),
    ("Gridlock traffic from town all the way to the bypass.", "Congestion", "Low")
]

FIRST_NAMES = ["John", "Mary", "David", "Sarah", "Kevin", "Grace", "Brian", "Fatuma", "Ali", "Dennis"]
LAST_NAMES = ["Kamau", "Ochieng", "Mutiso", "Hassan", "Njoroge", "Kiprono", "Otieno", "Abdi", "Mwangi"]

def seed_database(num_records=2000):
    # Ensure DB is wiped for a clean start
    import os
    if os.path.exists("grievances.db"):
        os.remove("grievances.db")
        print("🗑️ Old database removed.")

    init_db()  
    print(f"🚀 Injecting {num_records} realistic Nairobi records...")
    
    for i in range(num_records):
        # Sequential ID to guarantee no "IntegrityError"
        ticket_id = f"NRB-{100000 + i}"
        
        # Spread timestamps over 30 days
        random_minutes_ago = random.randint(1, 43200)
        timestamp = (datetime.now() - timedelta(minutes=random_minutes_ago)).strftime("%Y-%m-%d %H:%M")
        
        f_name = random.choice(FIRST_NAMES)
        l_name = random.choice(LAST_NAMES)
        
        sub_county, ward, landmark = random.choice(LOCATIONS)
        complaint_text, category, priority = random.choice(COMPLAINTS)
        
        # New simplified status logic
        status = random.choice(["Open", "In Progress", "Resolved"])
        
        # Mapping to the exact keys required by your database.py save_ticket function
        ticket_data = {
            "Ticket ID": ticket_id,
            "Timestamp": timestamp,
            "Name": f"{f_name} {l_name}",
            "Email": f"{f_name.lower()}@gmail.com",
            "Phone": f"07{random.randint(10000000, 99999999)}",
            "Sub-county": sub_county,
            "Ward": ward,
            "Landmark": landmark,
            "complaint_text": complaint_text,
            "Category": category,
            "AI Priority": priority,
            "Status": status
        }
        
        save_ticket(ticket_data)
        
        if (i + 1) % 500 == 0:
            print(f"✅ {i + 1} records processed...")

if __name__ == "__main__":
    seed_database(2000)
    print("✨ Seeding Complete. Your Dashboard is now live with 2,000 realistic records!")