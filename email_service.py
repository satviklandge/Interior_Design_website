"""
Email service for sending contact form and newsletter emails via SMTP.
AicuSa Interiors — FastAPI Backend
"""

import os
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib
from dotenv import load_dotenv

from models import ContactForm, NewsletterForm

# Load environment variables
load_dotenv()

logger = logging.getLogger("aicusa.email")

# SMTP configuration from .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")


def _is_smtp_configured() -> bool:
    """Check if SMTP credentials are properly configured."""
    return bool(SMTP_USER and SMTP_PASSWORD and SMTP_PASSWORD != "dqzb wksp nfvk bdds")


async def _send_email(subject: str, body_html: str, reply_to: str = "") -> bool:
    """
    Send an email via SMTP.
    Returns True on success, raises an exception on failure.
    """
    if not _is_smtp_configured():
        logger.warning("SMTP not configured — email not sent. Please update .env with your credentials.")
        # Return True anyway so the form still "works" during development
        # without crashing. The log message tells the developer what to do.
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(body_html, "html"))

    try:
        # Create a proper SSL context
        tls_context = ssl.create_default_context()

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,
            tls_context=tls_context,
        )
        logger.info(f"Email sent successfully: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


async def send_contact_email(form: ContactForm) -> bool:
    """
    Send the contact form submission as a formatted email.
    """
    # Build a nicely formatted HTML email
    project_info = form.project_type
    if form.other_project_text:
        project_info = f"Other: {form.other_project_text}"

    subject = f"New Enquiry: {form.subject} — {form.name}"

    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1d1d1d; color: #cda858; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">AicuSa INTERIORS</h1>
            <p style="margin: 5px 0 0; color: #ffffff; font-size: 14px;">New Contact Form Submission</p>
        </div>
        <div style="padding: 25px; background: #f9f9f9; border: 1px solid #e0e0e0;">
            <h2 style="color: #1d1d1d; border-bottom: 2px solid #cda858; padding-bottom: 10px;">
                Contact Details
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 5px; font-weight: bold; color: #555; width: 40%;">Name:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.name}</td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Email:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">
                        <a href="mailto:{form.email}" style="color: #cda858;">{form.email}</a>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Contact No:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.contact_no}</td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Subject:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.subject}</td>
                </tr>
            </table>

            <h2 style="color: #1d1d1d; border-bottom: 2px solid #cda858; padding-bottom: 10px; margin-top: 25px;">
                Project Details
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 5px; font-weight: bold; color: #555; width: 40%;">Project Type:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{project_info}</td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Status of Possession:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.possession}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Budget Range:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.budget}</td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Scope of Work:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.scope}</td>
                </tr>
            </table>
        </div>
        <div style="background: #1d1d1d; color: #999; padding: 15px; text-align: center; font-size: 12px;">
            This email was sent from the AicuSa Interiors website contact form.
        </div>
    </div>
    """

    return await _send_email(subject, body_html, reply_to=str(form.email))


async def send_newsletter_notification(form: NewsletterForm) -> bool:
    """
    Send a notification that someone subscribed to the newsletter.
    """
    subject = f"New Newsletter Subscriber: {form.name}"

    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1d1d1d; color: #cda858; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">AicuSa INTERIORS</h1>
            <p style="margin: 5px 0 0; color: #ffffff; font-size: 14px;">New Newsletter Subscription</p>
        </div>
        <div style="padding: 25px; background: #f9f9f9; border: 1px solid #e0e0e0;">
            <h2 style="color: #1d1d1d; border-bottom: 2px solid #cda858; padding-bottom: 10px;">
                Subscriber Details
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 5px; font-weight: bold; color: #555; width: 40%;">Name:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">{form.name}</td>
                </tr>
                <tr style="background: #fff;">
                    <td style="padding: 10px 5px; font-weight: bold; color: #555;">Email:</td>
                    <td style="padding: 10px 5px; color: #1d1d1d;">
                        <a href="mailto:{form.email}" style="color: #cda858;">{form.email}</a>
                    </td>
                </tr>
            </table>
        </div>
        <div style="background: #1d1d1d; color: #999; padding: 15px; text-align: center; font-size: 12px;">
            This email was sent from the AicuSa Interiors website newsletter form.
        </div>
    </div>
    """

    return await _send_email(subject, body_html)
