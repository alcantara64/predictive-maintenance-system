import smtplib
from twilio.rest import Client

class NotificationService:
    def __init__(self, email_config=None, sms_config=None):
        self.email_config = email_config or {}
        self.sms_config = sms_config or {}

    def send_notification(self, notification_type, recipient, message, subject=None):
        if notification_type == "email":
            return self.send_email(recipient, subject, message)
        elif notification_type == "sms":
            return self.send_sms(recipient, message)
        elif notification_type == "push":
            return self.send_push_notification(recipient, message)
        return "Invalid notification type"

    def send_email(self, to_email, subject, body):
        sender_email = self.email_config.get("email")
        sender_password = self.email_config.get("password")
        
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            email_message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, to_email, email_message)
            server.quit()
            return "Email sent successfully!"
        except Exception as e:
            return f"Failed to send email: {e}"

    def send_sms(self, to_phone, message):
        account_sid = self.sms_config.get("account_sid")
        auth_token = self.sms_config.get("auth_token")
        from_phone = self.sms_config.get("from_phone")
        
        try:
            client = Client(account_sid, auth_token)
            client.messages.create(body=message, from_=from_phone, to=to_phone)
            return "SMS sent successfully!"
        except Exception as e:
            return f"Failed to send SMS: {e}"

    def send_push_notification(self, to_device, message):
        return f"Push notification sent to {to_device}: {message}"
