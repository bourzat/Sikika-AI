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

def load_all_tickets():
    """Fetches all tickets and renames 'feedback' for the UI."""
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
            "feedback": "Feedback" # Rename for consistency in Tab 2/Tab 4
        }, inplace=True)
        tickets_list = df.to_dict(orient="records")
    except Exception:
        tickets_list = []
    
    conn.close()
    return tickets_list

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
