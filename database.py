import sqlite3
import pandas as pd

DB_NAME = "grievances.db"

def init_db():
    """Creates the database table with the Feedback column included."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            timestamp TEXT,
            name TEXT,
            email TEXT,
            phone TEXT,
            sub_county TEXT,
            ward TEXT,
            landmark TEXT,
            complaint_text TEXT,
            category TEXT,
            ai_priority TEXT,
            status TEXT,
            feedback TEXT DEFAULT '' 
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(ticket_data):
    """Inserts a new ticket with a placeholder for feedback."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (
            ticket_id, timestamp, name, email, phone, 
            sub_county, ward, landmark, complaint_text, category, ai_priority, status, feedback
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_data["Ticket ID"], ticket_data["Timestamp"], ticket_data["Name"], 
        ticket_data["Email"], ticket_data["Phone"], ticket_data["Sub-county"], 
        ticket_data["Ward"], ticket_data.get("Landmark", ""), 
        ticket_data["complaint_text"], ticket_data["Category"], 
        ticket_data["AI Priority"], ticket_data["Status"],
        "" # Default feedback is empty string
    ))
    conn.commit()
    conn.close()

def seed_data():
    """Adds a sample ticket so the dashboard isn't empty during the demo."""
    # Check if we already have tickets
    tickets = load_all_tickets()
    
    if len(tickets) == 0:
        # Create a sample dictionary that matches what save_ticket expects
        sample_ticket = {
            "Ticket ID": "NRB-101010",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Name": "Ilyas Bourzat",
            "Email": "bourzatilyas@gmail.com",
            "Phone": "0712345678",
            "Sub-county": "Westlands",
            "Ward": "Parklands/Highridge",
            "Landmark": "USIU-Africa Main Gate",
            "complaint_text": "Severe potholes making the road impassable near the university entrance.",
            "Category": "Potholes",
            "AI Priority": "High",
            "Status": "Open",
            "Feedback": ""
        }
        # Save it to the DB
        save_ticket(sample_ticket)

def update_ticket_status(tid, new_status, feedback=""):
    """Updates both status and feedback note."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets 
        SET status = ?, feedback = ? 
        WHERE ticket_id = ?
    ''', (new_status, feedback, tid))
    conn.commit()
    conn.close()
