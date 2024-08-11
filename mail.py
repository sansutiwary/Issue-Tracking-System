import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Email configuration
EMAIL_USER = 'sportsmsanskar@gmail.com'
EMAIL_PASS = 'manoj@1234'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
RECIPIENTS = ['2006128@kiit.ac.in', 'sanskarm17@gmail.com']

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output for SMTP
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        logging.info("Email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {e}")

# Test email functionality
subject = 'Test Email'
body = 'This is a test email to check the email functionality.'

send_email(subject, body)
