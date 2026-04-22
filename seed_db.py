import sqlite3
import random
from datetime import datetime, timedelta
from database import init_db

DB_NAME = "grievances.db"

# Realistic Nairobi Geodata
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

# Upgraded Complaints matching the new Kenyan Categories
COMPLAINTS = [
    ("Massive pothole causing traffic buildup and damaging tires.", "Potholes, Ruined Tarmac, Or Damaged Road Surface", "Medium", "Open 🟡"),
    ("Someone stole the manhole cover on the pavement, huge hazard.", "Stolen Manhole Covers, Missing Guardrails, Or Vandalized Streetlights", "Medium", "Open 🟡"),
    ("Traffic lights at the intersection have been dead since morning.", "Dead Traffic Lights, Missing Road Signs, Or Faded Paint", "Critical", "Escalated 🔴"),
    ("The drainage is completely blocked, road is flooded and impassable.", "Blocked Drainage Or Flooded Roads", "Critical", "Escalated 🔴"),
    ("Matatus are overlapping heavily on the pedestrian walkway.", "Matatu Overlapping, Boda Bodas On Sidewalks, Or Reckless Driving", "Medium", "Open 🟡"),
    ("A stalled lorry has blocked the left lane causing a huge jam.", "Stalled Trucks, Illegal Parking, Or Road Obstruction", "Medium", "Open 🟡"),
    ("Terrible accident between a bus and a personal car, road completely blocked.", "Vehicle Collision Or Severe Road Accident", "Critical", "Escalated 🔴"),
    ("They built a new speed bump but didn't paint it, cars are flying.", "Unmarked Speed Bumps Or Abandoned Road Construction", "High", "Escalated 🔴"),
    ("Gridlock traffic from town all the way to the bypass.", "Heavy Traffic Jam And General Congestion", "Low", "Logged 🟢")
]

FIRST_NAMES = [
    "John", "Mary", "David", "Sarah", "Kevin", "Grace", "Brian", "Fatuma", 
    "Ali", "Dennis", "Lucy", "Peter", "Jane", "Victor", "Joyce", "Emmanuel", 
    "Cynthia", "Collins", "Mercy", "Ian", "Felix", "Faith", "Eric", "Diana", "Kelvin"
]

LAST_NAMES = [
    "Kamau", "Ochieng", "Mutiso", "Hassan", "Njoroge", "Kiprono", "Otieno", "Abdi", 
    "Mwangi", "Odhiambo", "Kariuki", "Ndungu", "Kimani", "Onyango", "Maina", 
    "Kiptoo", "Kipkorir", "Wanjala", "Omondi", "Mutua", "Wamalwa", "Karanja", "Muriithi"
]

def seed_database(num_records=2000):
    # This guarantees the table actually exists before we insert data
    init_db()  
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print(f"Injecting {num_records} highly realistic Kenyan records into the database...")
    
    for i in range(num_records):
        # 100% mathematically guaranteed to be unique
        ticket_id = f"MOR-{100000 + i}"
        
        # Spread the timestamps over the last 30 days so it looks like a real timeline
        random_minutes_ago = random.randint(1, 43200)
        timestamp = (datetime.now() - timedelta(minutes=random_minutes_ago)).strftime("%Y-%m-%d %H:%M")
        
        # Dynamically generate unique names
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        # Make the emails look authentic
        if random.random() > 0.5:
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
        else:
            email = f"{first_name[0].lower()}{last_name.lower()}@gmail.com"
            
        phone = f"07{random.randint(10000000, 99999999)}"
        
        sub_county, ward, landmark = random.choice(LOCATIONS)
        text, category, priority, status = random.choice(COMPLAINTS)
        
        # Simulate that about 10% of these are marked as active hotspots
        is_hotspot = "⚠️ YES" if random.random() > 0.9 else "No"
        
        cursor.execute('''
            INSERT INTO tickets (
                ticket_id, timestamp, name, email, phone, 
                sub_county, ward, landmark, complaint_text, category, ai_priority, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, timestamp, name, email, phone, sub_county, ward, landmark, text, category, priority, status))
        
    conn.commit()
    conn.close()
    print("✅ 2000 Records successfully populated!")

if __name__ == "__main__":
    seed_database(2000)