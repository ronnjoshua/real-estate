from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Get Resend API key
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Only import and configure resend if API key is available
resend = None
if RESEND_API_KEY:
    try:
        import resend as resend_module
        resend_module.api_key = RESEND_API_KEY
        resend = resend_module
        logger.info("Resend configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Resend: {e}")
else:
    logger.warning("RESEND_API_KEY not set - email functionality disabled")

# Admin email addresses to receive contact form submissions
ADMIN_EMAILS = ["ronnnucup1@gmail.com", "ejdizon0618@gmail.com"]


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


@router.post("/", response_model=ContactResponse)
async def submit_contact_form(form: ContactForm):
    """
    Handle contact form submission.
    Sends email to admins and confirmation to the client.
    """
    if not resend or not RESEND_API_KEY:
        logger.error("RESEND_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service not configured. Please contact the administrator."
        )

    try:
        # Email to admins
        admin_email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #374151; }}
                .value {{ margin-top: 5px; padding: 10px; background-color: white; border-radius: 4px; border: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Contact Form Submission</h1>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Name:</div>
                        <div class="value">{form.name}</div>
                    </div>
                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value">{form.email}</div>
                    </div>
                    <div class="field">
                        <div class="label">Phone:</div>
                        <div class="value">{form.phone or "Not provided"}</div>
                    </div>
                    <div class="field">
                        <div class="label">Message:</div>
                        <div class="value">{form.message}</div>
                    </div>
                </div>
                <div class="footer">
                    This message was sent from your Real Estate website contact form.
                </div>
            </div>
        </body>
        </html>
        """

        # Send to admins
        admin_result = resend.Emails.send({
            "from": "Real Estate <onboarding@resend.dev>",
            "to": ADMIN_EMAILS,
            "subject": f"New Contact Form Submission from {form.name}",
            "html": admin_email_html
        })

        logger.info(f"Admin email sent: {admin_result}")

        # Confirmation email to client
        client_email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .message {{ background-color: #f0f9ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; background-color: #f9fafb; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Contacting Us!</h1>
                </div>
                <div class="content">
                    <p>Dear {form.name},</p>

                    <p>Thank you for reaching out to us. We have received your inquiry and our team will get back to you as soon as possible.</p>

                    <div class="message">
                        <strong>Your Message:</strong>
                        <p>{form.message}</p>
                    </div>

                    <p>We typically respond within 24-48 business hours. If your matter is urgent, please don't hesitate to call us directly.</p>

                    <p>Best regards,<br>The Real Estate Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated confirmation email. Please do not reply directly to this email.</p>
                    <p>&copy; 2024 Real Estate. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Send confirmation to client
        client_result = resend.Emails.send({
            "from": "Real Estate <onboarding@resend.dev>",
            "to": [form.email],
            "subject": "Thank You for Contacting Real Estate",
            "html": client_email_html
        })

        logger.info(f"Client confirmation email sent: {client_result}")

        return ContactResponse(
            success=True,
            message="Thank you for your message. We will get back to you soon!"
        )

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )
