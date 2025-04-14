import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import logger
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    """
    A service to send emails with optional attachments.
    """
    def __init__(self, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_email(self, subject: str, body: str, to_email: str, attachment_path: str = None):
        """
        Sends an email with an optional attachment.

        Parameters:
            subject (str): The subject of the email.
            body (str): The body of the email.
            to_email (str): The recipient's email address.
            attachment_path (str, optional): The path to the file to attach to the email.

        Returns:
            bool: Returns True if the email is sent successfully, False otherwise.
        """
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add the body to the email
        msg.attach(MIMEText(body, 'plain'))
        
        # Add an attachment if specified
        if attachment_path and os.path.isfile(attachment_path):
            try:
                # Open the file to be attached
                with open(attachment_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                    msg.attach(part)
                logger.info(f"Attachment {attachment_path} added to the email.")
            except Exception as e:
                logger.error(f"Failed to attach file {attachment_path}: {e}")
                return False

        try:
            # Set up the server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Encrypt the session
            server.login(self.smtp_user, self.smtp_password)  # Login to SMTP server

            # Send the email
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()  # Close the connection

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
