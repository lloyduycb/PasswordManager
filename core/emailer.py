import smtplib
from email.mime.text import MIMEText

def send_otp_email(to_email, otp_code):
    msg = MIMEText(f"Your OTP code is: {otp_code}")
    msg['Subject'] = "Your Login OTP"
    msg['From'] = "pmsotpsender123@gmail.com"
    msg['To'] = to_email

    # Replace with real SMTP creds or use environment variables
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "pmsotpsender123@gmail.com"
    sender_password = "zbbk damu moxx wlwu"

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
