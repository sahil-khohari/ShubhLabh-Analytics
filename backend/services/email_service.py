import os
import smtplib
from email.message import EmailMessage

def send_otp_email(receiver_email: str, otp: str) -> bool:
    """
    Sends an OTP to the provided email address using SMTP (e.g. Gmail).
    Returns True if successful, False otherwise.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "ShubhLabh360")

    if not all([smtp_host, smtp_port, smtp_username, smtp_password, smtp_from_email]):
        print("SMTP configuration is missing. Cannot send OTP email.")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Verification OTP - ShubhLabh360'
        msg['From'] = f"{smtp_from_name} <{smtp_from_email}>"
        msg['To'] = receiver_email
        msg.set_content(
            f"Hello,\n\n"
            f"Your verification code is: {otp}\n\n"
            f"This code will expire in 5 minutes.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"Best regards,\n"
            f"{smtp_from_name} Team"
        )

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        print(f"Successfully sent OTP email to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        # We catch all exceptions to prevent leaking SMTP credentials or causing 500 errors
        return False
