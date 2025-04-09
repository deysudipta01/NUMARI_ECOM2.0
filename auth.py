import smtplib
import random
from email.mime.text import MIMEText

# Generate a 6-digit OTP
otp = str(random.randint(100000, 999999))

# Sender email and password (use App Password if necessary)
EMAIL_ADDRESS = "sudiptadey877@gmail.com"
EMAIL_PASSWORD = "gnyj cfpt eezr ypjz"

# Receiver email
TO_EMAIL = "ukdey01@gmail.com"

# Email subject and body
subject = "Your OTP Code"
body = f"Your One-Time Password (OTP) is: {otp}\n\nUse this code to verify your email. It is valid for 5 minutes."

# Setup email content
msg = MIMEText(body)
msg["From"] = EMAIL_ADDRESS
msg["To"] = TO_EMAIL
msg["Subject"] = subject

try:
    # Connect to Gmail SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Secure connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())  # Send email

    print(f"OTP sent successfully to {TO_EMAIL}")

except Exception as e:
    print("Error:", e)
