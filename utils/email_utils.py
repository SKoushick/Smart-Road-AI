import os
import sys
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import SENDGRID_API_KEY, SENDGRID_SENDER_EMAIL

# Set up logging for email utility
logger = logging.getLogger(__name__)

def send_assignment_email(officer_email: str, complaint_details: dict) -> bool:
    """
    Sends an email to the assigned officer using SendGrid.
    """
    if not SENDGRID_API_KEY or not SENDGRID_SENDER_EMAIL:
        logger.error("SendGrid API key or sender email not configured.")
        return False

    # Extract details safely
    complaint_id = complaint_details.get("id", "Unknown")
    location = complaint_details.get("location_name", "Unknown Location")
    priority = complaint_details.get("severity_level", "Unknown Priority")
    description = complaint_details.get("description", "No description provided.")

    subject = "Smart Road Monitor – New Complaint Assigned"
    
    html_content = f"""
    <p>Dear Officer,</p>

    <p>A new road maintenance complaint has been assigned to you.</p>

    <ul>
        <li><strong>Complaint ID:</strong> {complaint_id}</li>
        <li><strong>Location:</strong> {location}</li>
        <li><strong>Priority:</strong> {priority}</li>
        <li><strong>Description:</strong> {description}</li>
    </ul>

    <p>Please log into the Smart Road Monitor dashboard to take action.</p>

    <p>Regards,<br>
    Smart Road Monitoring System</p>
    """

    message = Mail(
        from_email=SENDGRID_SENDER_EMAIL,
        to_emails=officer_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent successfully to {officer_email}. Status Code: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {officer_email}: {str(e)}")
        return False
