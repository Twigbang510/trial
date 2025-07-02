import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# Store temporary code (in production, use Redis)
verification_codes = {}

def generate_verification_code():
    """Generate 6 random numbers"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email: str, code: str, is_reset: bool = False):
    """Send email with verification code"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = email
        
        if is_reset:
            msg['Subject'] = "Password Reset Verification Code"
            body = f"""
        Hello,
        
        Your password reset verification code is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Trial Webapp Team
        """
        else:
            msg['Subject'] = "Email Verification Code"
            body = f"""
        Hello,
        
        Your email verification code is: {code}
        
        This code will expire in 10 minutes.
        
        Please enter this code to verify your account.
        
        Best regards,
        Trial Webapp Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect SMTP and send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.FROM_EMAIL, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_verification_code(email: str, code: str):
    """Store code in temporary memory"""
    verification_codes[email] = code

def verify_code(email: str, code: str):
    """Check if the code is correct"""
    stored_code = verification_codes.get(email)
    if stored_code and stored_code == code:
        # Delete code after successful verification
        del verification_codes[email]
        return True
    return False 