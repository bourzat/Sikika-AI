import sqlite3
import pandas as pd
from datetime import datetime # Added this for the seed timestamp

DB_NAME = "grievances.db"

def init_db():
    """Creates the database table with the correct schema."""
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

def seed_data():
    """Adds a sample ticket so the dashboard isn't empty during the demo."""
    tickets = load_all_tickets()
    if len(tickets) == 0:
        sample_ticket = {
            "Ticket ID": "NRB-101010",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Name": "Sikika Test User",
            "Email": "bourzatilyas@gmail.com",
            "Phone": "0712345678",
            "Sub-county": "Westlands",
            "Ward": "Parklands/Highridge",
            "Landmark": "USIU-Africa Main Gate",
            "complaint_text": "Potholes reported near the main university entrance.",
            "Category": "Potholes",
            "AI Priority": "High",
            "Status": "Open"
        }
        save_ticket(sample_ticket)

def save_ticket(ticket_data):
    """Inserts a new ticket."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (
            ticket_id, timestamp, name, email, phone, 
            sub_county, ward, landmark, complaint_text, category, ai_priority, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_data["Ticket ID"], ticket_data["Timestamp"], ticket_data["Name"], 
        ticket_data["Email"], ticket_data["Phone"], ticket_data["Sub-county"], 
        ticket_data["Ward"], ticket_data.get("Landmark", ""), 
        ticket_data["complaint_text"], ticket_data["Category"], 
        ticket_data["AI Priority"], ticket_data["Status"]
    ))
    conn.commit()
    conn.close()

def load_all_tickets():
    """Fetches tickets and renames columns for UI consistency."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM tickets", conn)
        df.rename(columns={
            "ticket_id": "Ticket ID", 
            "timestamp": "Timestamp", 
            "name": "Name",
            "email": "Email", 
            "phone": "Phone", 
            "sub_county": "Sub-county",
            "ward": "Ward", 
            "landmark": "Landmark", 
            "category": "Category", 
            "ai_priority": "AI Priority", 
            "status": "Status",
            "feedback": "Feedback"
        }, inplace=True)
        tickets_list = df.to_dict(orient="records")
    except Exception:
        tickets_list = []
    conn.close()
    return tickets_list

def update_ticket_status(tid, new_status, feedback=""):
    """Updates the status and feedback of a specific ticket."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets 
        SET status = ?, feedback = ? 
        WHERE ticket_id = ?
    ''', (new_status, feedback, tid))
    conn.commit()
    conn.close()
