import sqlite3
import pandas as pd

DB_NAME = "grievances.db"

def init_db():
    """Creates the database table if it doesn't exist yet."""
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
            landmark TEXT, -- <-- Added Landmark here
            complaint_text TEXT,
            category TEXT,
            ai_priority TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(ticket_data):
    """Inserts a single new ticket into the database."""
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
        ticket_data["Ward"], ticket_data.get("Landmark", ""), # <-- Added Landmark here
        ticket_data["complaint_text"], ticket_data["Category"], 
        ticket_data["AI Priority"], ticket_data["Status"]
    ))
    conn.commit()
    conn.close()

def load_all_tickets():
    """Fetches all tickets from the database and returns them as a list of dictionaries."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM tickets", conn)
        # Rename columns back to match the Streamlit state format
        df.rename(columns={
            "ticket_id": "Ticket ID", "timestamp": "Timestamp", "name": "Name",
            "email": "Email", "phone": "Phone", "sub_county": "Sub-county",
            "ward": "Ward", "landmark": "Landmark", "category": "Category", # <-- Added Landmark here
            "ai_priority": "AI Priority", "status": "Status"
        }, inplace=True)
        tickets_list = df.to_dict(orient="records")
    except pd.errors.DatabaseError:
        tickets_list = []
    
    conn.close()
    return tickets_list