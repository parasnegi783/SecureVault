import smtplib

smtp_server = 'smtp.gmail.com'
port = 587
sender_email = "parasnegi783@gmail.com"
password = "olay xbza rajw podo"
receiver_email = 'parasn456@gmail.com'
message = """\
Subject: Test Email

This is a test email from Python."""

try:
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print("Email sent successfully")
except Exception as e:
    print(f"Error: {e}")
