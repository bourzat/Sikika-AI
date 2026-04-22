import sqlite3
import pandas as pd

DB_NAME = "grievances.db"

def init_db():
    """Creates the database table with the correct schema if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # We use lowercase snake_case for the database columns for standard SQL practice
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
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(ticket_data):
    """Inserts a new ticket using keys from the Streamlit form dictionary."""
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
    """Fetches all tickets and renames columns to match the Dashboard's UI keys."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM tickets", conn)
        # We rename them here so Tab 2 and Tab 3 don't crash looking for 'AI Priority'
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
            "status": "Status"
        }, inplace=True)
        tickets_list = df.to_dict(orient="records")
    except Exception:
        tickets_list = []
    
    conn.close()
    return tickets_list

def update_ticket_status(tid, new_status):
    """Updates the status of a specific ticket in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Ensure the column name matches the CREATE TABLE statement (status)
    cursor.execute('''
        UPDATE tickets 
        SET status = ? 
        WHERE ticket_id = ?
    ''', (new_status, tid))
    conn.commit()
    conn.close()