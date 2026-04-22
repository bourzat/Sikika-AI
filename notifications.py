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