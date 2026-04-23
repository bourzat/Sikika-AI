import smtplib
from email.mime.text import MIMEText

def send_citizen_email(recipient_email, ticket_id, new_status, feedback=""):
    if not recipient_email or "@" not in recipient_email:
        return False
        
    sender = "bourzatilyas@gmail.com" # Put your Gmail here
    app_password = "yflbzyyzanoafvuu" # NO SPACES
    
    # Build the base message
    body = f"""Hello,

Your Ministry of Roads grievance (Ticket: {ticket_id}) has been updated.

Current Status: {new_status}
"""
    
    # Inject the feedback if the admin typed something
    if feedback.strip():
        body += f"\nResolution Notes: {feedback}\n"

    # Add the sign-off
    body += """
Thank you for helping us keep Nairobi moving.

- The Sikika AI Team"""
    
    msg = MIMEText(body)
    msg['Subject'] = f"Sikika AI Update: Ticket {ticket_id}"
    msg['From'] = sender
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


def send_submission_confirmation(ticket_data):
    """Sends a detailed receipt to the citizen immediately after they submit."""
    recipient_email = ticket_data["Email"]
    
    # Safety check
    if not recipient_email or "@" not in str(recipient_email):
        return False
        
    sender = "bourzatilyas@gmail.com" 
    app_password = "yflbzyyzanoafvuu"
    
    body = f"""Hello {ticket_data['Name']},

Thank you for reporting to Sikika AI. Your grievance has been successfully logged.

--- YOUR SUBMISSION DETAILS ---
Ticket ID: {ticket_data['Ticket ID']}
Category: {ticket_data['Category']}
Priority: {ticket_data['AI Priority']}
Location: {ticket_data['Ward']}, {ticket_data['Sub-county']}
Landmark: {ticket_data['Landmark']}

Complaint:
"{ticket_data['complaint_text']}"
-------------------------------

You can track the status of this ticket in the 'Track My Grievance' portal using your Ticket ID.

Keep Nairobi moving,
- The Sikika AI Team
"""
    
    msg = MIMEText(body)
    msg['Subject'] = f"Grievance Logged: {ticket_data['Ticket ID']}"
    msg['From'] = sender
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Confirmation email failed: {e}")
        return False
