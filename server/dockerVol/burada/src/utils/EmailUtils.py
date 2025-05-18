import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from dotenv import load_dotenv
import os

load_dotenv()

class EmailUtils:
    def __init__(self, smtp_server: str=None, smtp_port: int=587, username: str=None, password: str=None):
        self.smtp_server = os.getenv("SMTP_SERVER", smtp_server)
        self.smtp_port = int(os.getenv("SMTP_PORT", smtp_port))
        self.username = os.getenv("SMTP_USERNAME", username)
        self.password = os.getenv("SMTP_PASSWORD", password)
        self.useTLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.useSSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

    def send_email(self, to_email: str, subject: str, body_text: str=None, body_html: str=None, attachments=None):
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to_email
        message["Subject"] = subject

        # Plain text ekle
        # message.attach(MIMEText(body_text, "plain"))

        # Eğer HTML varsa onu da ekle
        if body_html:
            message.attach(MIMEText(body_html, "html", "utf-8"))

        # Attachments (isteğe bağlı)
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=file_path)
                part['Content-Disposition'] = f'attachment; filename="{file_path}"'
                message.attach(part)

        try:
            if self.useSSL:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.useTLS:
                        server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

class EmailTemplates:

    @staticmethod
    def get_mail_protection_start() -> str:
        """
        Generates the starting HTML for protected email content.
        The content inside this block will not be immediately visible when previewed externally.
        Returns:
            HTML (str): Mail protection start HTML content.
        """
        return """
        <div style="display:none;max-height:0;overflow:hidden;">
            This email requires proper rendering to be viewed correctly.
        </div>
        <div style="background-color: #121212; color: #ffffff; padding: 20px; border-radius: 8px; font-family: Arial, sans-serif;">
        <noscript>
            <div style="color: #ff5555; font-weight: bold;">
                This email requires JavaScript to display properly. Please enable it.
            </div>
        </noscript>
        <div style="filter: blur(8px); transition: filter 0.5s ease;" id="protected-content" onclick="this.style.filter='none'; this.style.cursor='default';">
            <p style="text-align: center; font-size: 18px; font-weight: bold;">Click to reveal protected content</p>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
            const content = document.getElementById('protected-content');content.addEventListener('mouseover', function() {this.style.cursor = 'pointer';});});
        </script>
        """

    @staticmethod
    def get_footer() -> str:
        """
        Returns:
            HTML (str): Footer HTML content.
        """
        return """
        <hr style="border:1px solid #555;">
        <p style="font-size:12px; color:#888; text-align:center;">
            This is an automated email. Please do not reply.
        </p>
        """

    @staticmethod
    def get_verification_email(verification_url: str) -> str:
        """
        Generates an HTML email template for email verification.

        Returns:
            HTML (str): HTML content for email verification.
        """
        return f"""
        <html>
            <body style="background-color:#1c1c1c; color:#f0f0f0; font-family:Arial, sans-serif; padding:20px;">
                {EmailTemplates.get_mail_protection_start()}
                <h2 style="color:#ffffff;">Verify Your Email Address</h2>
                <p>Please click the button below to verify your email address. This helps us secure your account.</p>
                
                <div style="text-align:center; margin:30px 0;">
                    <a href="{verification_url}" target="_blank" style="background-color:#4CAF50;color:white;padding:14px 25px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;border-radius:8px;">
                        Verify Email
                    </a>
                </div>

                <p>If the button does not work, copy and paste the link below into your browser:</p>
                <p style="word-break:break-all;">{verification_url}</p>

                {EmailTemplates.get_footer()}
            </body>
        </html>
        """

    @staticmethod
    def get_hello_mail(username: str) ->str:
        return f"""
        <div style="background-color: #121212; color: #ffffff; padding: 20px; border-radius: 8px; font-family: Arial, sans-serif;">
        {EmailTemplates.get_mail_protection_start()}
            <h2 style="text-align: center;">👋 Welcome, {username}!</h2>
            <p style="font-size: 16px; text-align: center;">
                We're excited to have you here. Thank you for joining our community!
            </p>
            <p style="font-size: 14px; text-align: center; margin-top: 20px;">
                Feel free to explore and reach out if you need any help.
            </p>
            <hr style="border-color: #333333; margin: 30px 0;">
            <p style="font-size: 12px; color: #aaaaaa; text-align: center;">
                This is an automated email. Please do not reply.
            </p>
        {EmailTemplates.get_footer()}
        </div>
        """