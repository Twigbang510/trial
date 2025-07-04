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

def send_booking_confirmation_email(email: str, booking_details: dict):
    """Send booking confirmation email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "🎓 Booking Confirmation - Appointment Scheduled"
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #332288; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .booking-card {{ background-color: #f8f9fa; border-left: 4px solid #332288; padding: 20px; margin: 20px 0; }}
        .detail-row {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #332288; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Booking Confirmation</h1>
        <p>Your appointment has been successfully scheduled!</p>
    </div>
    
    <div class="content">
        <h2>Dear,</h2>
        <p>Thank you for booking an appointment through our system. Your session has been confirmed with the following details:</p>
        
        <div class="booking-card">
            <h3>📅 Appointment Details</h3>
            <div class="detail-row">
                <span class="label">👨‍🏫 Lecturer:</span> {booking_details.get('lecturer_name', 'N/A')}
            </div>
            <div class="detail-row">
                <span class="label">📅 Date:</span> {booking_details.get('date', 'N/A')}
            </div>
            <div class="detail-row">
                <span class="label">⏰ Time:</span> {booking_details.get('time', 'N/A')}
            </div>
            <div class="detail-row">
                <span class="label">📚 Subject:</span> {booking_details.get('subject', 'N/A')}
            </div>
            <div class="detail-row">
                <span class="label">📍 Location:</span> {booking_details.get('location', 'TBD')}
            </div>
            <div class="detail-row">
                <span class="label">⏱️ Duration:</span> {booking_details.get('duration_minutes', 30)} minutes
            </div>
        </div>
        
        <h3>📝 Important Notes:</h3>
        <ul>
            <li>Please arrive 5 minutes before your scheduled time</li>
            <li>Bring all necessary materials and questions</li>
            <li>If you need to reschedule, please contact us at least 2 hours in advance</li>
            <li>Keep this email as your booking reference</li>
        </ul>
        
        <h3>📞 Need Help?</h3>
        <p>If you have any questions or need to make changes to your appointment, please contact our support team.</p>
    </div>
    
    <div class="footer">
        <p>This is an automated message. Please do not reply to this email.</p>
        <p><strong>Trial Webapp Team</strong></p>
        <p>© 2025 Educational Booking System. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect SMTP and send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.FROM_EMAIL, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
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