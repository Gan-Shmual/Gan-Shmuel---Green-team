import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def send_email(subject, body, is_success=True):
    sender_email = os.environ.get("GMAIL_USER")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient_emails = [
        e.strip() for e in os.environ.get("TEAM_EMAILS", "").split(",") if e.strip()
        ]

    if not sender_email or not sender_password:
        print("Email credentials not configured")
        return
    
    if not recipient_emails:
        print("No Recipient emails configured")
        return
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipient_emails)
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print(f"Email sent successfully to {', '.join(recipient_emails)}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_email.py <subject> <body> [success|failure]")
        sys.exit(1)
    
    subject = sys.argv[1]
    body = sys.argv[2]
    if len(sys.argv) > 3:
        status_arg = sys.argv[3].lower()
        is_success = status_arg == "success"
    else:
        is_success = True

    send_email(subject, body, is_success)